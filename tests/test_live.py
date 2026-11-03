"""Weekly canary against the live BOE API: `uv run pytest -m live` (skipped by default)."""

import asyncio
import xml.etree.ElementTree as ET
from datetime import datetime
from zoneinfo import ZoneInfo

import httpx
import pytest

from boe_rag_sync.aliases import LAWS
from boe_rag_sync.boe import fetch, parse_law
from boe_rag_sync.chunking import build_records

pytestmark = pytest.mark.live
WORKERS_STATUTE = "BOE-A-2015-11430"


async def _metadata(client: httpx.AsyncClient, law_id: str) -> ET.Element:
    root = ET.fromstring(await fetch(client, law_id, "metadatos"))  # noqa: S314
    meta = root.find("data/metadatos")
    assert meta is not None, law_id
    return meta


def test_every_alias_still_points_to_a_law_in_force() -> None:
    async def check() -> list[str]:
        async with httpx.AsyncClient(timeout=60) as client:
            problems = []
            for alias, (law_id, _) in LAWS.items():
                meta = await _metadata(client, law_id)
                if meta.findtext("estatus_derogacion") == "S":
                    problems.append(f"{alias} ({law_id}) is repealed")
            return problems

    assert asyncio.run(check()) == []


def test_a_live_law_still_parses_and_chunks() -> None:
    # Catches BOE format changes the fixtures cannot: structure, notes, sizes.
    async def download() -> tuple[bytes, bytes]:
        async with httpx.AsyncClient(timeout=60) as client:
            return await asyncio.gather(
                fetch(client, WORKERS_STATUTE, "metadatos"), fetch(client, WORKERS_STATUTE, "texto")
            )

    metadata, text = asyncio.run(download())
    records = build_records(
        parse_law(WORKERS_STATUTE, metadata, text),
        datetime.now(ZoneInfo("Europe/Madrid")).date(),
        2000,
    )
    assert len(records) > 200
    assert all(r["chars"] <= 2000 for r in records)
    a4 = next(r for r in records if r["block_id"] == "a4")
    assert "TÍTULO I. De la relación individual de trabajo" in a4["hierarchy"]
    assert a4["text"].startswith("**Artículo 4. Derechos laborales.**")
    text_all = " ".join(r["text"] for r in records)
    # Previous wordings live only in editorial notes: one in the text means notes leak.
    assert "Redacción anterior" not in text_all
    # The XML holds ~60 "Téngase en cuenta" consolidation notes; the one kept is a "(*)" footnote
    # of the 2015 text itself (transitional provision 7). Dozens would mean their markup changed.
    assert text_all.count("Téngase en cuenta") <= 1
