"""Turn parsed BOE blocks into RAG records."""

from datetime import date

from .boe import Block, Version


def version_at(block: Block, day: date) -> Version | None:
    in_force = [v for v in block.versions if v.in_force_from <= day]
    # max() keeps the first of equal keys; reversing makes the later version in document order win
    # when two versions share an entry-into-force date.
    return max(reversed(in_force), key=lambda v: v.in_force_from, default=None)


def build_records(law_id: str, blocks: list[Block], as_of: date) -> list[dict[str, str]]:
    records = []
    for block in blocks:
        version = version_at(block, as_of) if block.type == "precepto" else None
        if version is None:
            continue
        records.append(
            {
                "chunk_id": f"{law_id}:{block.id}:0",
                "law_id": law_id,
                "block_id": block.id,
                "version_norm_id": version.norm_id,
                "in_force_from": version.in_force_from.isoformat(),
                "text": "\n\n".join(version.paragraphs),
            }
        )
    return records
