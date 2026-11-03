"""Apify shell: the only module that talks to the platform."""

from datetime import date, datetime
from zoneinfo import ZoneInfo

import httpx
from apify import Actor

from .boe import fetch, parse_law
from .chunking import build_records

DEFAULT_MAX_CHUNK_CHARS = 2000
MIN_CHUNK_CHARS = 200


async def main() -> None:
    async with Actor:
        actor_input = await Actor.get_input() or {}
        as_of = _as_of(actor_input.get("asOfDate"))
        max_chars = _max_chars(actor_input.get("maxChunkChars", DEFAULT_MAX_CHUNK_CHARS))
        async with httpx.AsyncClient(timeout=60) as client:
            for law_id in actor_input["laws"]:
                law = parse_law(
                    law_id,
                    await fetch(client, law_id, "metadatos"),
                    await fetch(client, law_id, "texto"),
                )
                records = build_records(law, as_of, max_chars)
                # push_data takes plain dicts; a TypedDict is not a subtype of dict[Any, Any].
                await Actor.push_data([dict(record) for record in records])
                Actor.log.info("%s: %d chunks as of %s", law_id, len(records), as_of)


def _as_of(value: str | None) -> date:
    # BOE dates are Spanish calendar dates, so "today" is today in Spain.
    return date.fromisoformat(value) if value else datetime.now(ZoneInfo("Europe/Madrid")).date()


def _max_chars(value: object) -> int:
    # The platform validates against the input schema, but local runs and API calls with a raw
    # input do not; a tiny limit would explode one article into hundreds of chunks.
    if not isinstance(value, int) or value < MIN_CHUNK_CHARS:
        msg = f"maxChunkChars must be an integer >= {MIN_CHUNK_CHARS}, got {value!r}"
        raise ValueError(msg)
    return value
