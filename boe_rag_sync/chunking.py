"""Turn a parsed BOE law into RAG-ready records."""

import hashlib
import json
import math
import re
import uuid
from collections.abc import Iterable, Sequence
from datetime import date
from typing import Literal, TypedDict

from .aliases import SHORT_NAMES
from .boe import Block, Law, Table, Version

# Never change: every point_id derives from it, so a new namespace forces a full reload on users.
NAMESPACE = uuid.UUID("dcb6a199-8d7f-4d18-9e68-34e9f6b45dcf")
ATTRIBUTION = "Basado en datos de la Agencia Estatal Boletín Oficial del Estado"
DISCLAIMER = "Texto consolidado de carácter meramente informativo, sin valor jurídico."

_HEADING = re.compile(r"\*\*[^*]+\*\*")
_SENTENCE_END = re.compile(r'[.;:]\s+(?=[A-ZÁÉÍÓÚÑ\d«"(¿])')
_ABBREVIATION = re.compile(
    r"(?<!\w)(?:(?i:arts?|aptdo|apdo|cfr|dña|etc|núm|pág|párr|sra?|ss|vid)|[A-ZÁÉÍÓÚÑ])\.\Z"
)
# law_updated_at changes whenever any article of the law is reformed: hashing it would re-upsert
# every chunk of the law on each reform (ADR 0004).
_UNHASHED = frozenset({"op", "content_hash", "law_updated_at"})


class Record(TypedDict):
    op: Literal["upsert"]
    chunk_id: str
    point_id: str
    law_id: str
    law_title: str
    block_id: str
    block_type: str
    hierarchy: list[str]
    context_header: str
    text: str
    chunk_index: int
    chunk_count: int
    version_norm_id: str
    in_force_from: str
    in_force_until: str | None
    law_updated_at: str
    chars: int
    approx_tokens: int
    content_hash: str
    source_url: str
    attribution: str
    disclaimer: str


def version_at(block: Block, day: date) -> Version | None:
    in_force = [v for v in block.versions if v.in_force_from <= day]
    # Among the wordings already in force, the most recently published norm prevails (lex
    # posterior), which is what boe.es shows: income tax art. 7 has a norm published Oct 3 effective
    # Oct 23 and a later one published Oct 7 effective Oct 8, and the latter is the text in force.
    # The XML is not in date order. max() keeps the first of equal keys, so reversing makes the
    # later version in document order win a full tie.
    return max(reversed(in_force), key=_precedence, default=None)


def _precedence(version: Version) -> tuple[date, date]:
    return version.published, version.in_force_from


def split(content: Sequence[str | Table], max_chars: int) -> list[str]:
    if max_chars < 1:
        msg = f"max_chars must be positive, got {max_chars}"
        raise ValueError(msg)
    # (separator, text) pieces packed in a single greedy pass, so a short heading shares its chunk
    # with the first sentences of an oversize paragraph instead of becoming a chunk of its own.
    pieces: list[tuple[str, str]] = []
    for i, unit in enumerate(content):
        if isinstance(unit, Table):
            pieces += [("\n\n", part) for part in _split_table(unit, max_chars)]
        elif len(unit) <= max_chars and not _orphans_heading(
            content[i - 1] if i else None, unit, max_chars
        ):
            pieces.append(("\n\n", unit))
        else:
            pieces += _split_paragraph(unit, max_chars)
    return _pack(pieces, max_chars)


def _orphans_heading(previous: str | Table | None, paragraph: str, max_chars: int) -> bool:
    # Kept whole, this paragraph would leave the bold article heading alone in a chunk, which
    # retrieves nothing useful; split into sentences, its first sentence joins the heading.
    # ponytail: a heading still ends up alone when even the first sentence does not fit beside it
    # (0 chunks at 2000 chars, 52 of ~7,500 at 500 on five laws); moving the article name into
    # context_header would make such chunks droppable.
    return (
        isinstance(previous, str)
        and bool(_HEADING.fullmatch(previous))
        and len(previous) + 2 + len(paragraph) > max_chars
    )


def build_records(law: Law, as_of: date, max_chars: int) -> list[Record]:
    if law.repealed:
        return []
    records: list[Record] = []
    for block in law.blocks:
        version = version_at(block, as_of)
        if version is None or version.repealed or not version.content:
            continue
        chunks = split(version.content, max_chars)
        # A short name ("Ley del IRPF") carries the meaning of the official title in a few words.
        name = SHORT_NAMES.get(law.id, law.title)
        header = "[" + " > ".join(filter(None, (name, *block.hierarchy, block.title))) + "]"
        # Only a wording published later can displace this one (see version_at).
        until = min(
            (v.in_force_from for v in block.versions if _precedence(v) > _precedence(version)),
            default=None,
        )
        for index, text in enumerate(chunks):
            chunk_id = f"{law.id}:{block.id}:{index}"
            record = Record(
                op="upsert",
                chunk_id=chunk_id,
                point_id=point_id(chunk_id),
                law_id=law.id,
                law_title=law.title,
                block_id=block.id,
                block_type=block.type,
                hierarchy=list(block.hierarchy),
                context_header=header,
                text=text,
                chunk_index=index,
                chunk_count=len(chunks),
                version_norm_id=version.norm_id,
                in_force_from=version.in_force_from.isoformat(),
                in_force_until=None if until is None else until.isoformat(),
                law_updated_at=law.updated_at,
                chars=len(text),
                approx_tokens=math.ceil(len(text) / 4),
                content_hash="",
                source_url=f"https://www.boe.es/buscar/act.php?id={law.id}#{block.id}",
                attribution=ATTRIBUTION,
                disclaimer=DISCLAIMER,
            )
            record["content_hash"] = _content_hash(record)
            records.append(record)
    return records


def point_id(chunk_id: str) -> str:
    return str(uuid.uuid5(NAMESPACE, chunk_id))


def _split_paragraph(paragraph: str, max_chars: int) -> list[tuple[str, str]]:
    texts: list[str] = []
    for sentence in _sentences(paragraph):
        if len(sentence) <= max_chars:
            texts.append(sentence)
        else:
            # Packing words cuts at the last whitespace before the limit; only a word longer than
            # the limit is sliced.
            texts += [
                word[i : i + max_chars]
                for word in sentence.split()
                for i in range(0, len(word), max_chars)
            ]
    return [(" " if i else "\n\n", text) for i, text in enumerate(texts)]


def _sentences(paragraph: str) -> list[str]:
    sentences: list[str] = []
    start = 0
    for boundary in _SENTENCE_END.finditer(paragraph):
        sentence = paragraph[start : boundary.start() + 1]
        # A lone token such as the enumerator "1." or "Uno." opening a paragraph is not a sentence.
        if len(sentence.removeprefix("> ").split()) > 1 and not _ABBREVIATION.search(sentence):
            sentences.append(sentence)
            start = boundary.end()
    return [*sentences, paragraph[start:]]


def _split_table(table: Table, max_chars: int) -> list[str]:
    width = max(map(len, (table.header, *table.rows)))
    head = f"{_row(table.header, width)}\n|{' --- |' * width}"
    rows = [_row(row, width) for row in table.rows]
    whole = "\n".join([head, *rows])
    if len(whole) <= max_chars or not rows:
        return [whole]
    # A row that does not fit even alone under the header is packed alone, oversize. When the header
    # itself exceeds the limit every row ends up like that; the schema minimum (500) keeps that out
    # of the five laws measured (0 oversize chunks at 500, 59 at 200).
    bodies = _pack([("\n", row) for row in rows], max_chars - len(head) - 1)
    return [f"{head}\n{body}" for body in bodies]


def _row(cells: tuple[str, ...], width: int) -> str:
    padded = [cell.replace("|", r"\|") for cell in cells] + [""] * (width - len(cells))
    return f"| {' | '.join(padded)} |"


def _pack(pieces: Iterable[tuple[str, str]], max_chars: int) -> list[str]:
    chunks: list[str] = []
    for separator, text in pieces:
        if not text.strip():
            continue
        if chunks and len(chunks[-1]) + len(separator) + len(text) <= max_chars:
            chunks[-1] += separator + text
        else:
            chunks.append(text)
    return chunks


def _content_hash(record: Record) -> str:
    hashed = {key: value for key, value in record.items() if key not in _UNHASHED}
    canonical = json.dumps(hashed, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()
