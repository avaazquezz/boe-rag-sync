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
(e.g. `{"laws": ["BOE-A-2015-11430"]}`) and run `uv run python -m boe_rag_sync`; records land in
`storage/datasets/default/`.
Container: `docker build -t boe-rag-sync .`

## Architecture

Functional core, imperative shell. Only `main.py` (Apify) and `boe.fetch_text` (HTTP) do I/O;
everything else is pure and tested against fixtures.

- `boe.py` — fetch + parse XML into `Block`/`Version`
- `chunking.py` — version in force at a date, records (splitting arrives in phase 2)
- `sync.py` — manifest diff (phase 3)
- `main.py` — Apify shell

## Conventions

- Public contracts (input schema, record fields, `chunk_id`, `point_id` namespace) change only with a new ADR.
- New dependencies need the owner's approval.
- Fixtures are trimmed real BOE XML; never hand-written XML.
- BOE dates are Spanish calendar dates: "today" means today in Europe/Madrid.
- Code, comments, commits and docs in English; commits imperative, one line.
- Git flow: every change on its own branch from `main` (`feat/…`, `fix/…`, `docs/…`), pushed and opened
  as a PR. Nothing is committed straight to `main`; PRs are merged only after the owner approves them.
