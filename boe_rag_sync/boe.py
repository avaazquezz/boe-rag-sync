"""Fetch and parse consolidated legislation from the BOE open data API."""

import asyncio
import re
import xml.etree.ElementTree as ET
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import date, datetime
from typing import Literal

import httpx

API_URL = "https://www.boe.es/datosabiertos/api/legislacion-consolidada/id"
LAW_ID = re.compile(r"BOE-A-\d{4}-\d+")
ATTEMPTS = 4
RETRYABLE_STATUS = frozenset({429, 500, 502, 503, 504})

# Heading paragraph classes by nesting depth: a lower level encloses a higher one.
HEADING_LEVELS = {
    "anexo": 0,
    "libro_num": 1,
    "libro_tit": 1,
    "titulo": 2,
    "titulo_num": 2,
    "titulo_tit": 2,
    "capitulo": 3,
    "capitulo_num": 3,
    "capitulo_tit": 3,
    "seccion": 4,
    "subseccion": 5,
}
# Compared lower-cased: the Penal Code also uses "Cabecera" and "Encabezado".
HEADING_TYPES = frozenset({"encabezado", "cabecera"})
SKIPPED_TYPES = frozenset({"firma", "nota_inicial"})
TYPE_TITLES = {"preambulo": "Preámbulo", "parte_dispositiva": "Parte dispositiva"}
# The whole parenthesised marker ("(Suprimido)", "(Derogados)", "(Sin contenido)"), not an open
# citation such as "(derogado parcialmente por …)".
REPEALED = re.compile(r"\((?:suprimid|derogad|sin contenido|anulad)[a-z]*\)", re.IGNORECASE)
# Heading, optional heading subtitle (headings typed as articles) and the marker.
MAX_REPEALED_UNITS = 3
# Not "Disposiciones generales", which is an ordinary chapter title.
DISPOSITIONS_HEADING = re.compile(
    r"DISPOSICI(?:ÓN|ONES)\s+(?:ADICIONAL|TRANSITORIA|DEROGATORIA|FINAL)", re.IGNORECASE
)
# Inline elements also appear loose inside blockquotes (empty <ins/>, <span class="nota_pie">).
PARAGRAPH_TAGS = frozenset({"p", "ins", "strong", "em", "span", "a", "sup"})


@dataclass(frozen=True)
class Table:
    header: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]


@dataclass(frozen=True)
class Version:
    norm_id: str
    published: date
    in_force_from: date
    # Paragraphs (Markdown strings) and tables in document order, editorial notes removed.
    content: tuple[str | Table, ...]
    repealed: bool


@dataclass(frozen=True)
class Block:
    id: str
    type: str
    title: str
    # Enclosing headings, outermost first, e.g. ("TÍTULO I. De la relación…", "CAPÍTULO II. …").
    hierarchy: tuple[str, ...]
    versions: tuple[Version, ...]


@dataclass(frozen=True)
class Law:
    id: str
    title: str
    updated_at: str
    repealed: bool
    # Content blocks only: headings are folded into each block's hierarchy.
    blocks: tuple[Block, ...]


async def fetch(
    client: httpx.AsyncClient,
    law_id: str,
    resource: Literal["texto", "metadatos"],
    backoff: float = 1.0,
) -> bytes:
    # The id goes into the URL path: anything that is not a BOE id is rejected.
    if not LAW_ID.fullmatch(law_id):
        msg = f"Not a BOE law id: {law_id!r}"
        raise ValueError(msg)
    url = f"{API_URL}/{law_id}/{resource}"
    for attempt in range(ATTEMPTS):
        last = attempt == ATTEMPTS - 1
        try:
            response = await client.get(url, headers={"Accept": "application/xml"})
        except httpx.TransportError:
            if last:
                raise
        else:
            if last or response.status_code not in RETRYABLE_STATUS:
                response.raise_for_status()
                return response.content
        await asyncio.sleep(backoff * 2**attempt)
    raise AssertionError  # unreachable: the last attempt returns or raises


def parse_law(law_id: str, metadata_xml: bytes, text_xml: bytes) -> Law:
    meta = _xml(metadata_xml).find("data/metadatos")
    if meta is None:
        msg = f"{law_id}: no metadata in response"
        raise ValueError(msg)
    return Law(
        id=law_id,
        title=meta.findtext("titulo", "").strip().rstrip("."),
        updated_at=datetime.fromisoformat(meta.findtext("fecha_actualizacion", "")).isoformat(),
        repealed=any(
            meta.findtext(flag) == "S"
            for flag in ("estatus_derogacion", "estatus_anulacion", "vigencia_agotada")
        ),
        blocks=tuple(_blocks(_xml(text_xml))),
    )


def _xml(data: bytes) -> ET.Element:
    # <br/> separates words inside paragraphs and table cells; itertext() would glue them.
    data = re.sub(rb"<br\s*/?>", b" ", data)
    # Input comes only from the fixed BOE HTTPS endpoint, and expat >= 2.4.1 neither resolves
    # external entities nor allows entity expansion bombs, so defusedxml adds nothing here.
    return ET.fromstring(data)  # noqa: S314


def _blocks(root: ET.Element) -> Iterator[Block]:
    stack: list[tuple[int, str]] = []
    for element in root.iter("bloque"):
        kind = element.attrib["tipo"]
        # A version without an entry-into-force date never took effect (it was replaced before
        # its date arrived, e.g. Civil Code art. 56 in 2015).
        versions = [v for v in element.findall("version") if v.get("fecha_vigencia")]
        if kind.lower() in HEADING_TYPES:
            # The XML is not in date order: the latest wording is the one from the most recently
            # published norm (same rule as chunking.version_at). Penal Code s2-5 lists 2002 first.
            # ponytail: headings use their latest wording whatever the asOfDate; renamed
            # headings are rare. Version them like blocks if an eval shows it matters.
            latest = max(reversed(versions), key=_precedence, default=None)
            for level, label in _headings(latest) if latest is not None else []:
                stack = [h for h in stack if h[0] < level] + [(level, label)]
            continue
        if kind in SKIPPED_TYPES:
            continue
        title = element.get("titulo") or TYPE_TITLES.get(kind, element.attrib["id"])
        if title.startswith("Disposición"):
            # Dispositions sit outside titles and chapters, but most laws give them no heading
            # of their own, so the last chapter would otherwise leak into their path.
            stack = [h for h in stack if h[0] == 0 or _is_disposition_heading(h[1])]
        yield Block(
            id=element.attrib["id"],
            type=kind,
            title=title,
            hierarchy=tuple(label for _, label in stack),
            versions=tuple(_version(v, element.attrib["id"]) for v in versions),
        )


def _precedence(version: ET.Element) -> tuple[str, str]:
    # YYYYMMDD strings compare like dates.
    return version.attrib["fecha_publicacion"], version.attrib["fecha_vigencia"]


def _headings(version: ET.Element) -> list[tuple[int, str]]:
    """Heading labels of a heading block; one block can open several levels at once."""
    found: list[tuple[int, str]] = []
    for p in version.findall("p"):
        text = _text(p)
        level = HEADING_LEVELS.get(p.get("class", ""))
        # ponytail: other paragraphs in a heading block are dropped (only the Civil Code's
        # transitional provisions intro has some); emit them as a block if coverage needs it.
        if level is None or not text:
            continue
        if _is_disposition_heading(text):
            level = 1
        if found and found[-1][0] == level:
            found[-1] = (level, f"{found[-1][1]}. {text}")
        else:
            found.append((level, text))
    return found


def _is_disposition_heading(text: str) -> bool:
    return bool(DISPOSITIONS_HEADING.match(text))


def _version(element: ET.Element, block_id: str) -> Version:
    content = tuple(_content(element, block_id, quote=False))
    return Version(
        norm_id=element.attrib["id_norma"],
        published=date.fromisoformat(element.attrib["fecha_publicacion"]),
        in_force_from=date.fromisoformat(element.attrib["fecha_vigencia"]),
        content=content,
        repealed=_is_repealed(content),
    )


def _is_repealed(content: tuple[str | Table, ...]) -> bool:
    # A repealed block keeps only its heading and a marker: "(Suprimido)." on its own line or
    # inside the heading ("Sección 1.ª (Suprimida)"). A live article can still contain
    # "b) (Suprimida)." for one letter, which is neither.
    texts = [unit for unit in content if isinstance(unit, str)]
    return (
        bool(texts)
        and len(content) <= MAX_REPEALED_UNITS
        and (
            bool(REPEALED.search(texts[0])) or any(REPEALED.fullmatch(t.rstrip(".")) for t in texts)
        )
    )


def _content(parent: ET.Element, block_id: str, *, quote: bool) -> Iterator[str | Table]:
    for child in parent:
        if child.tag in PARAGRAPH_TAGS:
            text = _text(child)
            css = child.get("class", "")
            if not text or css.startswith("nota_pie"):
                continue
            if css == "articulo":
                text = f"**{text}**"
            yield f"> {text}" if quote else text
        elif child.tag == "blockquote":
            # A classed blockquote is an editorial note ("Téngase en cuenta…", often with the
            # previous wording); keeping it would put repealed text into the chunk.
            if "class" not in child.attrib:
                yield from _content(child, block_id, quote=True)
        elif child.tag == "table":
            table = _table(child)
            if table.header or table.rows:
                yield table
        else:
            msg = f"Unexpected <{child.tag}> in block {block_id}"
            raise ValueError(msg)


def _table(element: ET.Element) -> Table:
    # ponytail: rowspan/colspan are flattened (2 of 526 cells in the income tax law use them).
    rows = [
        cells
        for tr in element.iter("tr")
        if any(cells := tuple(_cell(c) for c in tr if c.tag in {"td", "th"}))
    ]
    if not rows:
        return Table(header=(), rows=())
    return Table(header=rows[0], rows=tuple(rows[1:]))


def _cell(cell: ET.Element) -> str:
    paragraphs = cell.findall("p")
    return " ".join(_text(p) for p in paragraphs) if paragraphs else _text(cell)


def _text(element: ET.Element) -> str:
    return " ".join("".join(element.itertext()).split())
