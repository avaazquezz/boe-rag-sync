# 1. Python, the Apify SDK and uv

Date: 2026-11-03 · Status: accepted

## Context

The Actor downloads a few XML files per run and transforms them; there is no crawling. The author's AI
stack (LangGraph, MCP servers, Qdrant) is Python, and the parsing/chunking core should be reusable there.

## Decision

Python 3.14 with the official `apify` SDK, `httpx` for HTTP and `xml.etree` from the standard library.
Dependencies managed with uv, following Apify's uv guide (package at the repo root, `pyproject.toml`,
`uv.lock`, Dockerfile on `apify/actor-python`). Tooling: pytest, ruff, mypy, pre-commit, GitHub Actions.

## Alternatives

- TypeScript + Crawlee: Apify's most common stack, but its value is crawling, which this Actor does not do,
  and it splits the author's codebase in two languages.
- lxml: faster, but BOE XML is well formed and at most ~4 MB per law; stdlib parses it in under a second.

## Consequences

The core has no Apify dependency and can be reused as a library. Python cold starts on Apify are slower
than Node, which is irrelevant for a weekly batch job.
