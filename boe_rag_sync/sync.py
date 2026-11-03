"""Turn the chunks a law produces now into the upserts and deletes that sync a store (ADR 0002)."""

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Literal, TypedDict

from .chunking import Record, point_id

# chunk_id -> content_hash of the last upsert emitted for that chunk.
type Manifest = dict[str, str]


class Delete(TypedDict):
    op: Literal["delete"]
    chunk_id: str
    point_id: str
    law_id: str
    # superseded: the block still has chunks, just fewer; repealed: it has none at asOfDate.
    reason: Literal["superseded", "repealed"]


type Op = Record | Delete


@dataclass(frozen=True)
class Change:
    """Every op of one block, emitted and billed together so no block is left half synced."""

    block_id: str
    ops: tuple[Op, ...]

    @property
    def billable(self) -> bool:
        return any(op["op"] == "upsert" for op in self.ops)


def diff(
    manifest: Mapping[str, str], records: Sequence[Record], *, full_reload: bool
) -> list[Change]:
    produced = {r["chunk_id"] for r in records}
    live_blocks = {r["block_id"] for r in records}
    by_block: dict[str, list[Op]] = {}
    for chunk_id in manifest:
        if chunk_id not in produced:
            # "{law_id}:{block_id}:{index}"; law ids are validated, block ids come from the XML.
            law_id, rest = chunk_id.split(":", 1)
            block_id = rest.rsplit(":", 1)[0]
            by_block.setdefault(block_id, []).append(
                Delete(
                    op="delete",
                    chunk_id=chunk_id,
                    point_id=point_id(chunk_id),
                    law_id=law_id,
                    reason="superseded" if block_id in live_blocks else "repealed",
                )
            )
    for record in records:
        if full_reload or manifest.get(record["chunk_id"]) != record["content_hash"]:
            by_block.setdefault(record["block_id"], []).append(record)
    return [Change(block_id, tuple(ops)) for block_id, ops in by_block.items()]


def within_budget(changes: Sequence[Change], affordable: int | None) -> tuple[list[Change], int]:
    """Changes to emit when only `affordable` billable blocks can be paid for (None: no limit).

    Free changes (deletes only) are always kept; billable ones in order while the budget lasts.
    Returns the kept changes and how many billable ones were left for a later run.
    """
    kept: list[Change] = []
    billable = left_out = 0
    for change in changes:
        if change.billable:
            if affordable is not None and billable >= affordable:
                left_out += 1
                continue
            billable += 1
        kept.append(change)
    return kept, left_out


def apply(manifest: Mapping[str, str], ops: Iterable[Op]) -> Manifest:
    """The manifest once `ops` reached the dataset; a run cut short records only what it emitted."""
    updated = dict(manifest)
    for op in ops:
        if op["op"] == "upsert":
            updated[op["chunk_id"]] = op["content_hash"]
        else:
            updated.pop(op["chunk_id"], None)
    return updated
