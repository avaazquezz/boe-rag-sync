# 3. Output record contract and chunk ids

Date: 2026-11-03 · Status: accepted

## Context

Users write records straight into a vector store and keep it in sync across runs, so ids and field names
are a public contract: changing them forces every user into a full reload.

The first proposal, `law:block:fecha_vigencia:index`, collides: Workers' Statute art. 37 has two versions
with the same `fecha_vigencia` (2026-10-23) from different norms. Qdrant also rejects string point ids
(only unsigned integers or UUIDs).

## Decision

- `chunk_id = {law_id}:{block_id}:{i}` — stable per block; a reform overwrites the same ids and deletes
  surplus indices.
- `point_id = uuid5(NAMESPACE, chunk_id)` with a namespace fixed in code, ready for Qdrant.
- Upsert record: `op, chunk_id, point_id, law_id, law_title, block_id, block_type, hierarchy,
  context_header, text, chunk_index, chunk_count, version_norm_id, in_force_from, in_force_until,
  law_updated_at, chars, approx_tokens, content_hash, source_url, attribution, disclaimer`.
- Delete record: `op, chunk_id, point_id, law_id, reason` with `reason ∈ {superseded, repealed}`.
- `context_header` and `text` are separate fields; the user decides whether to embed the header.
- Field names and enum values in English.
- `content_hash` = SHA-256 of the canonical JSON of the record without `op` (superseded by ADR 0004).
- `point_id` namespace, fixed in code: `dcb6a199-8d7f-4d18-9e68-34e9f6b45dcf`.

## Alternatives

- Version in the id (`law:block@version:i`): needed only for history output, which is out of v1. If history
  is added it gets its own id scheme so current-only users are unaffected.
- One flag to prepend the header to `text`: one more option to test for something the user can do in one line.

## Consequences

Ids depend on `maxChunkChars`; changing it produces deletes for old ids and upserts for new ones (handled
by ADR 0002). The namespace UUID must never change.
