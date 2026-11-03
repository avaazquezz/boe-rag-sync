# 4. The content hash excludes law_updated_at

Date: 2026-11-03 · Status: accepted · Supersedes the `content_hash` definition in ADR 0003

## Context

ADR 0003 defined `content_hash` over the whole record except `op`. The record includes `law_updated_at`,
the date the BOE last updated the consolidated text of the *law*. That date changes whenever any article
of the law is reformed. With it in the hash, one reform of one article would change the hash of every
chunk of the law, so the sync (ADR 0002) would re-upsert, and bill, the whole law.

## Decision

`content_hash` = `"sha256:"` + SHA-256 of the canonical JSON (sorted keys, no extra whitespace, UTF-8,
non-ASCII kept) of the record without `op`, `content_hash` and `law_updated_at`.

## Alternatives

- Keep `law_updated_at` hashed: correct per chunk, but turns every reform into a full reload.
- Drop `law_updated_at` from the record: the BOE reuse conditions require stating the date of the last
  update of the consolidated text.

## Consequences

`law_updated_at` stored with a chunk is the law's update date when that chunk was last emitted, not the
latest one. Consumers that need the law's current update date read it from the most recent records of
that law.
