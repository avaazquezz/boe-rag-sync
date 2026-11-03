"""End to end on real BOE XML: parse_law output feeds build_records."""

from datetime import date
from functools import cache
from pathlib import Path

from boe_rag_sync.boe import parse_law
from boe_rag_sync.chunking import Record, build_records

FIXTURES = Path(__file__).parent / "fixtures"
LAW_IDS = {
    "et": "BOE-A-2015-11430",
    "cc": "BOE-A-1889-4763",
    "cp": "BOE-A-1995-25444",
    "irpf": "BOE-A-2006-20764",
}
TODAY = date(2026, 11, 3)


@cache
def records(name: str, as_of: date = TODAY, max_chars: int = 2000) -> list[Record]:
    law = parse_law(
        LAW_IDS[name],
        (FIXTURES / f"{name}_meta.xml").read_bytes(),
        (FIXTURES / f"{name}_texto.xml").read_bytes(),
    )
    return build_records(law, as_of, max_chars)


def of_block(name: str, block_id: str, as_of: date = TODAY) -> list[Record]:
    return [r for r in records(name, as_of) if r["block_id"] == block_id]


def test_picks_the_wording_in_force_at_the_date() -> None:
    (old,) = of_block("et", "a4", as_of=date(2023, 3, 1))
    assert old["version_norm_id"] == "BOE-A-2015-11430"
    assert old["in_force_until"] == "2023-03-02"
    # Two norms reworded art. 37 from the same day; the later one in the XML prevails.
    assert {r["version_norm_id"] for r in of_block("et", "a37")} == {"BOE-A-2026-21872"}


def test_repealed_articles_produce_no_records() -> None:
    assert of_block("cp", "a88") == []
    assert of_block("cc", "as127a130") == []


def test_context_header_carries_the_whole_path() -> None:
    (a4,) = of_block("et", "a4")
    assert a4["context_header"] == (
        "[Real Decreto Legislativo 2/2015, de 23 de octubre, por el que se aprueba el texto "
        "refundido de la Ley del Estatuto de los Trabajadores > TEXTO REFUNDIDO DE LA LEY DEL "
        "ESTATUTO DE LOS TRABAJADORES > TÍTULO I. De la relación individual de trabajo > "
        "CAPÍTULO I. Disposiciones generales > Sección 2.ª Derechos y deberes laborales básicos "
        "> Artículo 4]"
    )
    assert a4["text"].startswith("**Artículo 4. Derechos laborales.**\n\n1. Los trabajadores")


def test_long_disposition_splits_within_the_limit_without_losing_text() -> None:
    chunks = of_block("irpf", "dfsegunda")
    assert len(chunks) > 20
    assert all(r["chars"] <= 2000 for r in chunks)
    assert [r["chunk_index"] for r in chunks] == list(range(len(chunks)))
    assert {r["chunk_count"] for r in chunks} == {len(chunks)}


def test_tables_survive_as_markdown() -> None:
    text = "\n".join(r["text"] for r in of_block("irpf", "a52"))
    assert "| Importe anual de la contribución | Aportación máxima del trabajador |" in text
    assert "| Más de 1.500 euros. | El resultado de multiplicar la contribución" in text


def test_editorial_notes_never_reach_the_text() -> None:
    text = " ".join(r["text"] for name in LAW_IDS for r in records(name))
    assert "Redacción anterior" not in text
    assert "Téngase en cuenta" not in text


def test_chunk_ids_are_unique() -> None:
    ids = [r["chunk_id"] for name in LAW_IDS for r in records(name, max_chars=500)]
    assert len(ids) == len(set(ids))
