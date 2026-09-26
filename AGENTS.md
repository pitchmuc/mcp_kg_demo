# Contributor Guide

This project is a Python 3.12 backend service built with FastMCP and rdflib.
All source code lives under `src/kg_mcp_server` and tests live under `tests`.

## Development Environment
- Use [uv](https://github.com/astral-sh/uv) to create and manage the virtual environment.
  - `uv venv --python 3.12`
  - `source .venv/bin/activate`
- Sync dependencies including dev extras with `uv sync --all-extras`.
- When editing or running the server manually use `mcp run src/kg_mcp_server/server.py`.

## Domain model

The knowledge graph is a Turtle file at `data/knowledge_graph.ttl` using the
`crm:` namespace (`http://example.org/crm#`). It contains two classes:

- `crm:Account` — a fictional enterprise customer (industry, tier, region,
  ARR, employee count, health score, renewal date, owner, website).
- `crm:Contact` — a fictional person (`crm:worksAt` an Account; job title,
  sales role, email, phone, champion flag, sentiment, last contacted date).

All data is synthetic. Do not add real company or personal data.

## Testing Instructions
- Run unit tests with `pytest` from the repository root.
- Ensure linting passes with `ruff check .`.
- Run static type checks using `mypy src tests`.
- All three steps (`ruff`, `mypy`, and `pytest`) should succeed before committing.

## PR Instructions
- Use concise commit messages.
- Title pull requests using the format `[kg-mcp-server] <brief description>`.
- Describe any manual testing steps performed and mention whether `pytest`, `ruff`, and `mypy` passed.

There is currently no frontend code in this repository. If a frontend is
added in the future, document how to run and test it within this file.
