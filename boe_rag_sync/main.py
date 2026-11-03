"""Apify shell: the only module that talks to the platform."""

import asyncio
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any
from zoneinfo import ZoneInfo

import httpx
from apify import Actor
from apify.storages import KeyValueStore

from .aliases import resolve
from .boe import fetch, parse_law
from .chunking import build_records
from .sync import Manifest, apply, diff, within_budget

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
    full_reload: bool
    billing: bool
    # Manifest key prefix: the syncId, plus the date when asOfDate pins one, so a one-off run at a
    # past date never rewrites the state of the store that follows the law day by day.
    state_prefix: str


async def main() -> None:
    async with Actor:
        actor_input = await Actor.get_input() or {}
        pricing = Actor.get_charging_manager().get_pricing_info()
        if pricing.per_event_prices.get(DATASET_ITEM_EVENT):
            msg = f"{DATASET_ITEM_EVENT} must stay unpriced: charge only {BILLED_EVENT!r}"
            raise RuntimeError(msg)
        pinned = actor_input.get("asOfDate")
        sync_id = actor_input.get("syncId", DEFAULT_SYNC_ID)
        settings = Settings(
            as_of=date.fromisoformat(pinned) if pinned else _today(),
            max_chars=actor_input.get("maxChunkChars", DEFAULT_MAX_CHUNK_CHARS),
            full_reload=actor_input.get("fullReload", False),
            billing=pricing.is_pay_per_event,
            state_prefix=f"{sync_id}.{pinned}" if pinned else sync_id,
        )
        # Resolved up front: a typo fails the run before any work or charge.
        law_ids = list(dict.fromkeys(resolve(ref) for ref in actor_input["laws"]))
        state = await Actor.open_key_value_store(name=STATE_STORE)
        results: list[dict[str, Any]] = []
        async with httpx.AsyncClient(timeout=60) as client:
            for law_id in law_ids:
                try:
                    result = await _sync_law(client, state, law_id, settings)
                except Exception as error:  # noqa: BLE001
                    # One broken law must not block the others; the run still fails below.
                    Actor.log.exception("%s: sync failed; nothing was charged for it", law_id)
                    result = {"law_id": law_id, "status": "failed", "error": repr(error)}
                results.append(result)
        await Actor.set_value(
            "OUTPUT",
            {"as_of": settings.as_of.isoformat(), "state": settings.state_prefix, "laws": results},
        )
        if any(r["status"] == "stopped_by_spending_limit" for r in results):
            await Actor.set_status_message("Spending limit reached; run again to sync the rest.")
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
    key = f"{settings.state_prefix}.{law_id}"
    manifest: Manifest = await state.get_value(key, {})
    affordable = (
        Actor.get_charging_manager().calculate_max_event_charge_count_within_limit(BILLED_EVENT)
        if settings.billing
        else None
    )
    changes, left_out = within_budget(
        diff(manifest, records, full_reload=settings.full_reload), affordable
    )
    ops = [op for change in changes for op in change.ops]

    # Deliver, record, then bill. If the run dies at any point before the charge (the platform
    # aborts soon after the spending limit, an API call fails), the user got data for free; the
    # opposite order could bill them twice for the same articles.
    for start in range(0, len(ops), PUSH_BATCH):
        # push_data takes plain dicts; a TypedDict is not a subtype of dict[Any, Any].
        await Actor.push_data([dict(op) for op in ops[start : start + PUSH_BATCH]])
    await state.set_value(key, apply(manifest, ops))
    charged = 0
    if settings.billing and (billable := sum(change.billable for change in changes)):
        charged = (await Actor.charge(BILLED_EVENT, count=billable)).charged_count
        if charged < billable:
            Actor.log.warning("%s: %d articles delivered, %d charged", law_id, billable, charged)

    upserts = sum(op["op"] == "upsert" for op in ops)
    status = "stopped_by_spending_limit" if left_out else "synced"
    Actor.log.info(
        "%s: %d upserts, %d deletes, %d articles charged, %d left for later (%s)",
        law_id,
        upserts,
        len(ops) - upserts,
        charged,
        left_out,
        status,
    )
    return {
        "law_id": law_id,
        "status": status,
        "upserts": upserts,
        "deletes": len(ops) - upserts,
        "articles_charged": charged,
        "articles_left_for_later": left_out,
        "chunks_in_force": len(records),
    }


def _today() -> date:
    # BOE dates are Spanish calendar dates, so "today" is today in Spain.
    return datetime.now(ZoneInfo("Europe/Madrid")).date()
