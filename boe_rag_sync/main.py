"""Apify shell: the only module that talks to the platform."""

import asyncio
from datetime import date, datetime
from zoneinfo import ZoneInfo

import httpx
from apify import Actor

from .boe import fetch, parse_law
from .chunking import build_records

# The platform validates input and applies schema defaults; this one serves local runs and must
# match .actor/input_schema.json (tests/test_main.py checks it).
DEFAULT_MAX_CHUNK_CHARS = 2000


async def main() -> None:
    async with Actor:
        actor_input = await Actor.get_input() or {}
        as_of = _as_of(actor_input.get("asOfDate"))
        max_chars = actor_input.get("maxChunkChars", DEFAULT_MAX_CHUNK_CHARS)
        async with httpx.AsyncClient(timeout=60) as client:
            for law_id in actor_input["laws"]:
                metadata, text = await asyncio.gather(
                    fetch(client, law_id, "metadatos"), fetch(client, law_id, "texto")
                )
                records = build_records(parse_law(law_id, metadata, text), as_of, max_chars)
                # push_data takes plain dicts; a TypedDict is not a subtype of dict[Any, Any].
                await Actor.push_data([dict(record) for record in records])
                Actor.log.info("%s: %d chunks as of %s", law_id, len(records), as_of)


def _as_of(value: str | None) -> date:
    # BOE dates are Spanish calendar dates, so "today" is today in Spain.
    return date.fromisoformat(value) if value else datetime.now(ZoneInfo("Europe/Madrid")).date()
