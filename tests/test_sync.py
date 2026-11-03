from datetime import date

from boe_rag_sync.boe import Block, Law, Version
from boe_rag_sync.chunking import Record, build_records, point_id
from boe_rag_sync.sync import Change, apply, diff

LAW_ID = "BOE-A-2015-11430"
TODAY = date(2026, 11, 3)
# Paragraphs of 80 characters with a 100-character limit: one chunk per paragraph.
MAX_CHARS = 100


def paragraphs(word: str, count: int) -> tuple[str, ...]:
    return tuple(f"{i}. {word} ".ljust(80, "x") for i in range(count))


def article(block_id: str, *content: str, repealed: bool = False) -> Block:
    version = Version(
        norm_id=LAW_ID,
        published=date(2015, 10, 24),
        in_force_from=date(2015, 11, 13),
        content=content,
        repealed=repealed,
    )
    return Block(id=block_id, type="precepto", title=block_id, hierarchy=(), versions=(version,))


def records(*blocks: Block, updated_at: str = "2026-10-01T00:00:00+00:00") -> list[Record]:
    law = Law(id=LAW_ID, title="Ley", updated_at=updated_at, repealed=False, blocks=blocks)
    return build_records(law, TODAY, MAX_CHARS)


def summary(changes: list[Change]) -> list[tuple[str, list[tuple[str, str]]]]:
    """(block, [(op, chunk index or delete reason)]) for readable assertions."""
    return [
        (
            change.block_id,
            [
                (
                    op["op"],
                    op["chunk_id"].rsplit(":", 1)[1] if op["op"] == "upsert" else op["reason"],
                )
                for op in change.ops
            ],
        )
        for change in changes
    ]


def sync(manifest: dict[str, str], current: list[Record]) -> tuple[list[Change], dict[str, str]]:
    changes = diff(manifest, current, full_reload=False)
    return changes, apply(manifest, (op for change in changes for op in change.ops))


def test_four_weeks_of_a_law() -> None:
    a52 = article("a52", *paragraphs("despido", 1))

    # Week 1, full load: everything is new.
    changes, manifest = sync({}, records(article("a4", *paragraphs("derechos", 2)), a52))
    assert summary(changes) == [
        ("a4", [("upsert", "0"), ("upsert", "1")]),
        ("a52", [("upsert", "0")]),
    ]

    # Week 2, art. 4 reformed and now 3 chunks: same ids overwritten plus a new one.
    changes, manifest = sync(manifest, records(article("a4", *paragraphs("reforma", 3)), a52))
    assert summary(changes) == [("a4", [("upsert", "0"), ("upsert", "1"), ("upsert", "2")])]

    # Week 3, art. 52 repealed: its chunk is deleted.
    a4 = article("a4", *paragraphs("reforma", 3))
    repealed = article("a52", "**Artículo 52.**", "(Derogado).", repealed=True)
    changes, manifest = sync(manifest, records(a4, repealed))
    assert summary(changes) == [("a52", [("delete", "repealed")])]

    # Week 4, nothing changed: nothing emitted, nothing billed.
    changes, manifest = sync(manifest, records(a4, repealed))
    assert changes == []
    assert manifest == {r["chunk_id"]: r["content_hash"] for r in records(a4)}


def test_a_shrinking_block_deletes_its_surplus_chunks_before_upserting() -> None:
    _, manifest = sync({}, records(article("a4", *paragraphs("largo", 3))))
    changes, manifest = sync(manifest, records(article("a4", *paragraphs("corto", 1))))
    assert summary(changes) == [
        ("a4", [("delete", "superseded"), ("delete", "superseded"), ("upsert", "0")])
    ]
    assert changes[0].billable
    assert list(manifest) == [f"{LAW_ID}:a4:0"]


def test_deletes_carry_the_point_id_the_store_knows() -> None:
    _, manifest = sync({}, records(article("a4", *paragraphs("texto", 1))))
    (change,) = diff(manifest, [], full_reload=False)
    assert change.ops == (
        {
            "op": "delete",
            "chunk_id": f"{LAW_ID}:a4:0",
            "point_id": point_id(f"{LAW_ID}:a4:0"),
            "law_id": LAW_ID,
            "reason": "repealed",
        },
    )
    assert not change.billable


def test_a_law_wide_update_date_alone_changes_nothing() -> None:
    # ADR 0004: law_updated_at moves whenever any article is reformed.
    _, manifest = sync({}, records(article("a4", *paragraphs("texto", 2))))
    later = records(article("a4", *paragraphs("texto", 2)), updated_at="2026-11-02T00:00:00+00:00")
    assert diff(manifest, later, full_reload=False) == []


def test_full_reload_re_emits_everything_and_still_deletes_stale_chunks() -> None:
    current = records(article("a4", *paragraphs("texto", 2)))
    _, manifest = sync({}, current)
    stale = {**manifest, f"{LAW_ID}:a99:0": "sha256:old"}
    assert summary(diff(stale, current, full_reload=True)) == [
        ("a99", [("delete", "repealed")]),
        ("a4", [("upsert", "0"), ("upsert", "1")]),
    ]


def test_a_tampered_manifest_is_repaired() -> None:
    current = records(article("a4", *paragraphs("texto", 2)))
    _, manifest = sync({}, current)
    tampered = {**manifest, f"{LAW_ID}:a4:1": "sha256:wrong"}
    changes, repaired = sync(tampered, current)
    assert summary(changes) == [("a4", [("upsert", "1")])]
    assert repaired == manifest


def test_apply_records_only_the_changes_that_were_emitted() -> None:
    # A run stopped by the spending limit after the first block: the next run must redo the rest.
    current = records(article("a1", *paragraphs("uno", 1)), article("a2", *paragraphs("dos", 1)))
    first, _ = diff({}, current, full_reload=False)
    partial = apply({}, first.ops)
    assert summary(diff(partial, current, full_reload=False)) == [("a2", [("upsert", "0")])]
