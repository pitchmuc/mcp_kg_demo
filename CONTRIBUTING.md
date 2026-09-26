# Contributing

Thanks for your interest in improving the Knowledge Graph MCP Server!

## Development setup

```bash
uv venv --python 3.12
source .venv/bin/activate   # Windows: .venv\Scripts\activate
uv sync --all-extras
```

## Before opening a PR

All three checks must pass:

```bash
ruff check .
mypy src tests
pytest
```

## Adding data to the knowledge graph

Edit `data/knowledge_graph.ttl` directly (it's plain Turtle/RDF). Keep all
data fictional — do not add real company or personal data. Follow the
existing `crm:` namespace and property set documented in
`src/kg_mcp_server/tools/schema.py` and `AGENTS.md`.

## Adding a new MCP tool

1. Add the function in `src/kg_mcp_server/tools/` (new or existing module).
2. Decorate with `@mcp.tool(annotations=ToolAnnotations(...))`.
3. Build SPARQL queries against the shared `crm:` namespace; always run them
   through `kg_mcp_server.graph.store.run_select_query`.
4. Import and re-export the function in `server.py` (`__all__`).
5. Add tests under `tests/`.

## Commit / PR conventions

- Concise, imperative commit messages (e.g. `Add search_accounts tool`).
- PR title format: `[kg-mcp-server] <brief description>`.
- Mention in the PR description whether `ruff`, `mypy`, and `pytest` passed.
