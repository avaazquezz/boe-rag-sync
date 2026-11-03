from datetime import date
from pathlib import Path

from boe_rag_sync.boe import Block, parse_blocks
from boe_rag_sync.chunking import build_records, version_at

FIXTURE = Path(__file__).parent / "fixtures" / "et_excerpt.xml"
LAW_ID = "BOE-A-2015-11430"


def block(block_id: str) -> Block:
    return next(b for b in parse_blocks(FIXTURE.read_bytes()) if b.id == block_id)


def norm_at(block_id: str, day: date) -> str | None:
    version = version_at(block(block_id), day)
    return version.norm_id if version else None


def test_version_at_picks_the_version_in_force() -> None:
    assert norm_at("a4", date(2015, 11, 12)) is None
    assert norm_at("a4", date(2023, 3, 1)) == "BOE-A-2015-11430"
    assert norm_at("a4", date(2023, 3, 2)) == "BOE-A-2023-5366"
    assert norm_at("a4", date(2026, 11, 3)) == "BOE-A-2023-15135"


def test_version_at_breaks_date_ties_by_document_order() -> None:
    # Two norms set new wording for art. 37 from the same day; the later one in the XML prevails.
    assert norm_at("a37", date(2026, 10, 23)) == "BOE-A-2026-21872"


def test_build_records_emits_one_record_per_article_in_force() -> None:
    blocks = parse_blocks(FIXTURE.read_bytes())
    records = build_records(LAW_ID, blocks, date(2026, 11, 3))
    assert [r["chunk_id"] for r in records] == [f"{LAW_ID}:{b}:0" for b in ("a1", "a4", "a37")]
    assert records[1]["text"].startswith("Artículo 4. Derechos laborales.\n\n1. ")
