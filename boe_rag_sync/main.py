"""Apify shell: the only module that talks to the platform."""

from datetime import date, datetime
from zoneinfo import ZoneInfo

import httpx
from apify import Actor

from .boe import fetch_text, parse_blocks
from .chunking import build_records


async def main() -> None:
    async with Actor:
        actor_input = await Actor.get_input() or {}
        as_of = _as_of(actor_input.get("asOfDate"))
        async with httpx.AsyncClient(timeout=60) as client:
            for law_id in actor_input["laws"]:
                blocks = parse_blocks(await fetch_text(client, law_id))
                records = build_records(law_id, blocks, as_of)
                await Actor.push_data(records)
                Actor.log.info("%s: %d records as of %s", law_id, len(records), as_of)


def _as_of(value: str | None) -> date:
    # BOE dates are Spanish calendar dates, so "today" is today in Spain.
    return date.fromisoformat(value) if value else datetime.now(ZoneInfo("Europe/Madrid")).date()
