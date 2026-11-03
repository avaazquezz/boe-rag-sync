# 2. Stateful sync with a manifest in a named key-value store

Date: 2026-11-03 · Status: accepted

## Context

Incremental mode must tell the user which chunks to delete, not only which to add. The first idea was
stateless: the user passes `sinceDate`, the Actor rebuilds the law as of that date and as of today from
today's XML, and emits the difference.

That rebuild assumes today's XML filtered to a past date equals what the XML looked like on that date.
It does not hold: the BOE adds versions to the consolidated text after they are published (and sometimes
after they enter into force) and corrects errata in place, and the API does not expose when a version was
consolidated. Example: a reform in force on Oct 23 is consolidated on Oct 29. A user who synced on Oct 25
got the old text; rebuilding "as of Oct 25" from today's XML already yields the new text, the diff is
empty, and the user keeps the outdated article forever.

## Decision

The Actor stores, in a named key-value store in the user's Apify account (`boe-rag-sync-state`, retained
indefinitely), one record per `(syncId, law)` with `{chunk_id: content_hash}` of what it last emitted.
Each run diffs the current chunks against that manifest: new or changed hash → `upsert`; missing →
`delete`. `fullReload` re-emits every current chunk.

## Alternatives

- Stateless diff with `sinceDate` (above): no storage, but silently wrong, and sync correctness is the
  product.
- Let the user diff: pushes the hardest part of the product onto the buyer.

## Consequences

- Removes `sinceDate` and the date-window logic from the input and the code.
- Changing `maxChunkChars` no longer needs a manual full reload: old ids are deleted, new ones upserted.
- The manifest records what was emitted, not what the user ingested; if the user's loader fails or their
  store is wiped, they run with `fullReload`.
- Delivery is at-least-once (a crash before the manifest write re-emits records); records are idempotent,
  so re-applying them is harmless.
