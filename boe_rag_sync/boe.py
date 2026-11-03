"""Fetch and parse consolidated legislation from the BOE open data API."""

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import date

import httpx

API_URL = "https://www.boe.es/datosabiertos/api/legislacion-consolidada/id"
LAW_ID = re.compile(r"BOE-A-\d{4}-\d+")


@dataclass(frozen=True)
class Version:
    norm_id: str
    published: date
    in_force_from: date
    paragraphs: tuple[str, ...]


@dataclass(frozen=True)
class Block:
    id: str
    type: str
    title: str
    versions: tuple[Version, ...]


async def fetch_text(client: httpx.AsyncClient, law_id: str) -> bytes:
    # The id goes into the URL path: anything that is not a BOE id is rejected.
    if not LAW_ID.fullmatch(law_id):
        msg = f"Not a BOE law id: {law_id!r}"
        raise ValueError(msg)
    response = await client.get(f"{API_URL}/{law_id}/texto", headers={"Accept": "application/xml"})
    response.raise_for_status()
    return response.content


def parse_blocks(xml: bytes) -> list[Block]:
    # Input comes only from the fixed BOE HTTPS endpoint, and expat >= 2.4.1 neither resolves
    # external entities nor allows entity expansion bombs, so defusedxml adds nothing here.
    root = ET.fromstring(xml)  # noqa: S314
    return [
        Block(
            id=block.attrib["id"],
            type=block.attrib["tipo"],
            title=block.get("titulo", ""),
            versions=tuple(_version(v) for v in block.iter("version")),
        )
        for block in root.iter("bloque")
    ]


def _version(element: ET.Element) -> Version:
    texts = (
        " ".join("".join(p.itertext()).split())
        for p in element.iter("p")
        if not p.get("class", "").startswith("nota_pie")
    )
    return Version(
        norm_id=element.attrib["id_norma"],
        published=date.fromisoformat(element.attrib["fecha_publicacion"]),
        in_force_from=date.fromisoformat(element.attrib["fecha_vigencia"]),
        paragraphs=tuple(t for t in texts if t),
    )
