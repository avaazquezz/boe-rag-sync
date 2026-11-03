# 5. Incremental sync is opt-in through syncId

Date: 2026-11-03 · Status: accepted · Amends the input contract of ADR 0002

## Context

`syncId` defaulted to `"default"`, so every run, including the first one anybody tries, kept state and
emitted only changes. Apify Store tests every public Actor daily with its prefilled input and requires a
successful run with a **non-empty** default dataset; more than half of the runs failing over three days
labels the Actor "Under maintenance", then "Deprecated". With a stateful default the test passes on day
one and then gets an empty dataset every day the laws do not change, which is most days.

## Decision

`syncId` has no default. Without it a run is a one-off export: it emits an upsert for every chunk, neither
reads nor writes the manifest and does not create the state store. With it, sync works as in ADR 0002.

## Alternatives

- Prefill `fullReload: true`: the test would pass, but every user opening the form would get it checked
  and a task saved from it would re-emit, and later bill, every article on every run.
- Ask Apify to skip the tests: discretionary, and it removes the Store's health signal for the Actor.

## Consequences

- A first-time user always gets data; incremental sync is something you turn on deliberately.
- A schedule without `syncId` exports (and, once paid, bills) everything each run; the README and the
  input description say `syncId` is required for scheduled runs.
- The daily Store test runs a stateless export of the prefilled law (Workers' Statute, about 5 s).
