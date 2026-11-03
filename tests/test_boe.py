import asyncio
from datetime import date
from pathlib import Path

import httpx
import pytest

from boe_rag_sync.boe import Block, fetch_text, parse_blocks

FIXTURE = Path(__file__).parent / "fixtures" / "et_excerpt.xml"


def blocks_by_id() -> dict[str, Block]:
    return {b.id: b for b in parse_blocks(FIXTURE.read_bytes())}


def test_parse_blocks_keeps_document_order_and_types() -> None:
    blocks = parse_blocks(FIXTURE.read_bytes())
    assert [b.id for b in blocks] == ["ti", "ci", "s1", "a1", "s2", "a4", "a37"]
    assert [b.type for b in blocks] == ["encabezado"] * 3 + ["precepto", "encabezado"] + [
        "precepto"
    ] * 2


def test_parse_blocks_reads_every_version() -> None:
    a4 = blocks_by_id()["a4"]
    assert [v.norm_id for v in a4.versions] == [
        "BOE-A-2015-11430",
        "BOE-A-2023-5366",
        "BOE-A-2023-15135",
    ]
    assert a4.versions[1].published == date(2023, 3, 1)
    assert a4.versions[1].in_force_from == date(2023, 3, 2)
    assert a4.versions[0].paragraphs[0] == "Artículo 4. Derechos laborales."


def test_parse_blocks_drops_editorial_notes() -> None:
    a4 = blocks_by_id()["a4"]
    assert not any(p.startswith("Se modifica") for v in a4.versions for p in v.paragraphs)


def test_fetch_text_rejects_non_boe_ids() -> None:
    async def call() -> bytes:
        async with httpx.AsyncClient() as client:
            return await fetch_text(client, "BOE-A-2015-11430/../metadatos")

    with pytest.raises(ValueError, match="Not a BOE law id"):
        asyncio.run(call())
