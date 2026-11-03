"""Apify shell: the only module that talks to the platform."""

import asyncio
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any
from zoneinfo import ZoneInfo

import httpx
from apify import Actor
from apify.storages import KeyValueStore

from .boe import fetch, parse_law
from .chunking import build_records
from .sync import Op, apply, diff

# The platform validates input and applies schema defaults; these serve local runs and must
# match .actor/input_schema.json (tests/test_main.py checks it).
DEFAULT_MAX_CHUNK_CHARS = 2000
DEFAULT_SYNC_ID = "default"
# Named storages outlive runs; with limited permissions the Actor keeps access to the stores it
# created in earlier runs of the same user (ADR 0002).
STATE_STORE = "boe-rag-sync-state"
BILLED_EVENT = "article"
# Apify's synthetic per-item event. Priced, it makes push_data drop items at the spending limit
# while the manifest would record them as emitted, so the user's store would never get them.
DATASET_ITEM_EVENT = "apify-default-dataset-item"
PUSH_BATCH = 500


@dataclass(frozen=True)
class Settings:
    as_of: date
    max_chars: int
    sync_id: str
    full_reload: bool
    billing: bool


async def main() -> None:
    async with Actor:
        actor_input = await Actor.get_input() or {}
        pricing = Actor.get_charging_manager().get_pricing_info()
        if pricing.per_event_prices.get(DATASET_ITEM_EVENT):
            msg = f"{DATASET_ITEM_EVENT} must stay unpriced: charge only {BILLED_EVENT!r}"
            raise RuntimeError(msg)
        settings = Settings(
            as_of=_as_of(actor_input.get("asOfDate")),
            max_chars=actor_input.get("maxChunkChars", DEFAULT_MAX_CHUNK_CHARS),
            sync_id=actor_input.get("syncId", DEFAULT_SYNC_ID),
            full_reload=actor_input.get("fullReload", False),
            billing=pricing.is_pay_per_event,
        )
        state = await Actor.open_key_value_store(name=STATE_STORE)
        results: list[dict[str, Any]] = []
        stopped = False
        async with httpx.AsyncClient(timeout=60) as client:
            for law_id in actor_input["laws"]:
                if stopped:
                    results.append({"law_id": law_id, "status": "skipped"})
                    continue
                try:
                    result = await _sync_law(client, state, law_id, settings)
                except Exception as error:  # noqa: BLE001
                    # One broken law must not block the others; the run still fails below.
                    Actor.log.exception("%s: sync failed, its manifest is untouched", law_id)
                    result = {"law_id": law_id, "status": "failed", "error": repr(error)}
                results.append(result)
                stopped = result["status"] == "stopped_by_spending_limit"
        await Actor.set_value(
            "OUTPUT",
            {
                "as_of": settings.as_of.isoformat(),
                "sync_id": settings.sync_id,
                "full_reload": settings.full_reload,
                "laws": results,
            },
        )
        if stopped:
            await Actor.set_status_message("Stopped at the spending limit; run again to resume.")
        if failed := [r["law_id"] for r in results if r["status"] == "failed"]:
            msg = f"Sync failed for {', '.join(failed)}; see the log and the OUTPUT record"
            raise RuntimeError(msg)


async def _sync_law(
    client: httpx.AsyncClient, state: KeyValueStore, law_id: str, settings: Settings
) -> dict[str, Any]:
    metadata, text = await asyncio.gather(
        fetch(client, law_id, "metadatos"), fetch(client, law_id, "texto")
    )
    records = build_records(parse_law(law_id, metadata, text), settings.as_of, settings.max_chars)
    key = f"{settings.sync_id}.{law_id}"
    manifest: dict[str, str] = await state.get_value(key, {})

    accepted: list[Op] = []
    pushed = charged = 0
    status = "synced"
    for change in diff(manifest, records, full_reload=settings.full_reload):
        limit_reached = False
        if settings.billing and change.billable:
            charge = await Actor.charge(BILLED_EVENT)
            if not charge.charged_count:
                status = "stopped_by_spending_limit"
                break
            charged += 1
            limit_reached = charge.event_charge_limit_reached
        accepted += change.ops
        # The platform aborts the run soon after the limit is reached: whatever was paid for is
        # pushed at once rather than left in memory.
        if limit_reached or len(accepted) - pushed >= PUSH_BATCH:
            await _push(accepted[pushed:])
            pushed = len(accepted)
        if limit_reached:
            status = "stopped_by_spending_limit"
            break
    await _push(accepted[pushed:])
    # Written after the push: a crash in between re-emits the same idempotent ops next run.
    await state.set_value(key, apply(manifest, accepted))

    upserts = sum(op["op"] == "upsert" for op in accepted)
    Actor.log.info(
        "%s: %d upserts, %d deletes, %d articles charged (%s)",
        law_id,
        upserts,
        len(accepted) - upserts,
        charged,
        status,
    )
    return {
        "law_id": law_id,
        "status": status,
        "upserts": upserts,
        "deletes": len(accepted) - upserts,
        "articles_charged": charged,
        "chunks_in_force": len(records),
    }


async def _push(ops: Sequence[Op]) -> None:
    if ops:
        # push_data takes plain dicts; a TypedDict is not a subtype of dict[Any, Any].
        await Actor.push_data([dict(op) for op in ops])


def _as_of(value: str | None) -> date:
    # BOE dates are Spanish calendar dates, so "today" is today in Spain.
    return date.fromisoformat(value) if value else datetime.now(ZoneInfo("Europe/Madrid")).date()
