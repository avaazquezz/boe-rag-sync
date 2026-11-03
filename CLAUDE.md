# boe-rag-sync

Apify Actor (Python) that turns Spanish consolidated laws from the BOE open data API into RAG-ready
chunks and keeps a vector store in sync with `upsert`/`delete` records.
Design: `docs/design.md`. Decisions: `docs/adr/`. Read both before changing contracts.

## Commands

```bash
uv sync                          # install (dev group included)
uv run pytest                    # tests (offline, real BOE XML fixtures in tests/fixtures)
uv run ruff format && uv run ruff check --fix
uv run mypy boe_rag_sync         # strict
uv run pre-commit install        # once per clone: format, lint, types and tests on commit
```

Run locally without the Apify CLI: put the input in `storage/key_value_stores/default/INPUT.json`
(e.g. `{"laws": ["BOE-A-2015-11430"]}`) and run `uv run python -m boe_rag_sync`; ops land in
`storage/datasets/default/`, the run summary in `storage/key_value_stores/default/OUTPUT` and the sync
manifests in `storage/key_value_stores/boe-rag-sync-state/` (they persist across runs; delete them to start
over). To simulate billing, pass real prices or every event (dataset items included) costs $1 locally:
`ACTOR_TEST_PAY_PER_EVENT=true ACTOR_MAX_TOTAL_CHARGE_USD=0.005 APIFY_CHARGED_ACTOR_EVENT_COUNTS='{"article": 0}'
APIFY_ACTOR_PRICING_INFO='{"pricingModel":"PAY_PER_EVENT","apifyMarginPercentage":0.2,"createdAt":"2026-11-01T00:00:00Z",
"startedAt":"2026-11-01T00:00:00Z","pricingPerEvent":{"actorChargeEvents":{"article":{"eventTitle":"Article",
"eventPriceUsd":0.001},"apify-default-dataset-item":{"eventTitle":"Item","eventPriceUsd":0}}}}'`.
The event counts must be non-empty: the SDK treats `{}` as missing and silently ignores the prices.
Container: `docker build -t boe-rag-sync .`

## Architecture

Functional core, imperative shell. Only `main.py` (Apify) and `boe.fetch` (HTTP, retries) do I/O;
everything else is pure and tested against fixtures.

- `boe.py` — fetch + `parse_law`: XML into `Law`/`Block`/`Version`/`Table`, hierarchy rebuilt from
  heading blocks, editorial notes dropped, repeals flagged. The BOE XML quirks it absorbs are listed in
  `docs/design.md`; read them before touching the parser.
- `chunking.py` — version in force at a date (lex posterior, see design.md), cascade splitting, records per ADR 0003 and 0004
- `sync.py` — `diff` (ops per block) and `apply` (manifest after what was emitted), pure
- `aliases.py` — alias → (BOE id, short name) for 20 common laws; `resolve` accepts id, URL or alias
- `main.py` — Apify shell

Tests: `test_boe.py` (parser on fixtures, fetch retries), `test_chunking.py` (splitter and records
on hand-built objects), `test_pipeline.py` (fixture XML → records), `test_sync.py` (four weeks of a
law, partial runs), `test_main.py` (local defaults match the input schema). Fixtures are trimmed from
real laws: Workers' Statute (`et`), Civil Code (`cc`), Penal Code (`cp`), income tax law (`irpf`).

## Conventions

- Public contracts (input schema, record fields, `chunk_id`, `point_id` namespace) change only with a new ADR.
- New dependencies need the owner's approval.
- Fixtures are trimmed real BOE XML; never hand-written XML.
- BOE dates are Spanish calendar dates: "today" means today in Europe/Madrid.
- Code, comments, commits and docs in English; commits imperative, one line.
- Git flow: every change on its own branch from `main` (`feat/…`, `fix/…`, `docs/…`), pushed and opened
  as a PR. Nothing is committed straight to `main`; PRs are merged only after the owner approves them.
