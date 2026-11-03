import asyncio
from collections.abc import Callable
from functools import cache
from pathlib import Path

import httpx
import pytest

from boe_rag_sync.boe import ATTEMPTS, Block, Law, Table, fetch, parse_law

FIXTURES = Path(__file__).parent / "fixtures"
LAW_IDS = {
    "et": "BOE-A-2015-11430",
    "cc": "BOE-A-1889-4763",
    "cp": "BOE-A-1995-25444",
    "irpf": "BOE-A-2006-20764",
}
ET_TEXT = "TEXTO REFUNDIDO DE LA LEY DEL ESTATUTO DE LOS TRABAJADORES"


@cache
def law(name: str) -> Law:
    return parse_law(
        LAW_IDS[name],
        (FIXTURES / f"{name}_meta.xml").read_bytes(),
        (FIXTURES / f"{name}_texto.xml").read_bytes(),
    )


def block(name: str, block_id: str) -> Block:
    return next(b for b in law(name).blocks if b.id == block_id)


def texts(name: str, block_id: str) -> list[str]:
    return [u for u in block(name, block_id).versions[-1].content if isinstance(u, str)]


def test_parse_law_reads_metadata() -> None:
    et = law("et")
    assert et.title.startswith("Real Decreto Legislativo 2/2015, de 23 de octubre")
    assert et.title.endswith("Ley del Estatuto de los Trabajadores")
    assert et.updated_at == "2026-10-29T08:21:56+00:00"
    assert not et.repealed


def test_headings_become_hierarchy_not_blocks() -> None:
    # Headings, the signature and the initial note are not content blocks.
    assert [b.id for b in law("et").blocks] == ["a1", "a4", "a37", "daprimera"]
    assert block("et", "a4").hierarchy == (
        ET_TEXT,
        "TÍTULO I. De la relación individual de trabajo",
        "CAPÍTULO I. Disposiciones generales",
        "Sección 2.ª Derechos y deberes laborales básicos",
    )


def test_penal_code_heading_types_cabecera_and_encabezado_are_headings() -> None:
    assert [b.id for b in law("cp").blocks] == ["a88", "a225", "a225bis", "a445"]
    assert block("cp", "a225bis").hierarchy[-1] == (
        "Sección 2.ª Del abandono de familia, menores o incapaces"
    )
    assert block("cp", "a445").hierarchy[-1].startswith("CAPÍTULO X.")


def test_one_heading_block_can_open_two_levels() -> None:
    # Civil Code "TÍTULO III" carries its first section in the same block.
    assert block("cc", "art657").hierarchy[-2:] == (
        "TÍTULO III. De las sucesiones",
        "Disposiciones generales",
    )


def test_dispositions_leave_titles_and_chapters() -> None:
    # No heading precedes them, so the last chapter must not leak into their path.
    assert block("et", "daprimera").hierarchy == (ET_TEXT,)
    assert block("irpf", "a108").hierarchy == ("TÍTULO XIII. Orden jurisdiccional",)
    assert block("irpf", "daprimera").hierarchy == ()
    # "DISPOSICIONES TRANSITORIAS" heading replaces books and titles; "Disposiciones
    # generales" (an ordinary chapter title) does not.
    assert block("cc", "primera").hierarchy == ("CÓDIGO CIVIL", "DISPOSICIONES TRANSITORIAS")


def test_article_heading_is_bold() -> None:
    assert block("et", "a4").versions[0].content[:2] == (
        "**Artículo 4. Derechos laborales.**",
        (
            "1. Los trabajadores tienen como derechos básicos, con el contenido y alcance que "
            "para cada uno de los mismos disponga su específica normativa, los de:"
        ),
    )


def test_editorial_notes_are_dropped() -> None:
    # Notes often carry the previous wording; keeping them would leak repealed text.
    assert not any(t.startswith("Se modifica") for t in texts("et", "a4"))
    a7 = " ".join(texts("irpf", "a7"))
    assert "Téngase en cuenta" not in a7
    assert "Redacción anterior" not in a7


def test_repealed_blocks_are_flagged() -> None:
    assert block("cp", "a88").versions[-1].repealed
    assert block("cc", "as127a130").versions[-1].repealed
    assert not block("et", "a4").versions[-1].repealed


def test_tables_are_structured() -> None:
    tables = [u for u in block("irpf", "a52").versions[-1].content if isinstance(u, Table)]
    assert len(tables) == 1
    assert tables[0].header == (
        "Importe anual de la contribución",
        "Aportación máxima del trabajador",
    )
    assert len(tables[0].rows) == 3


def run_fetch(
    handler: Callable[[httpx.Request], httpx.Response], law_id: str = "BOE-A-2015-11430"
) -> bytes:
    async def call() -> bytes:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await fetch(client, law_id, "texto", backoff=0)

    return asyncio.run(call())


def test_fetch_rejects_non_boe_ids() -> None:
    with pytest.raises(ValueError, match="Not a BOE law id"):
        run_fetch(lambda _: httpx.Response(200), "BOE-A-2015-11430/../metadatos")


def test_fetch_retries_server_errors_and_connection_failures() -> None:
    calls: list[int] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(1)
        if len(calls) == 1:
            msg = "connection refused"
            raise httpx.ConnectError(msg, request=request)
        if len(calls) == 2:
            return httpx.Response(503)
        return httpx.Response(200, content=b"<ok/>")

    assert run_fetch(handler) == b"<ok/>"
    assert len(calls) == 3


def test_fetch_does_not_retry_client_errors() -> None:
    calls: list[int] = []

    def handler(_: httpx.Request) -> httpx.Response:
        calls.append(1)
        return httpx.Response(400)

    with pytest.raises(httpx.HTTPStatusError):
        run_fetch(handler)
    assert len(calls) == 1


def test_fetch_gives_up_after_the_last_attempt() -> None:
    calls: list[int] = []

    def handler(_: httpx.Request) -> httpx.Response:
        calls.append(1)
        return httpx.Response(503)

    with pytest.raises(httpx.HTTPStatusError):
        run_fetch(handler)
    assert len(calls) == ATTEMPTS
