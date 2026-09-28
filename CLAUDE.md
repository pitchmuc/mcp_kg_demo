# CLAUDE.md — Knowledge Graph MCP Server

## Project Overview

This is a **Model Context Protocol (MCP) server** that exposes a fictional
CRM-style **knowledge graph** — enterprise **Accounts** and customer
**Contacts** — for querying by Claude, ChatGPT, Adobe Coworker, or any other
MCP-compatible client. The graph is a Turtle/RDF file loaded into memory with
`rdflib` and queried via SPARQL.

- **Language**: Python 3.12+
- **Framework**: FastMCP (from the `mcp` package)
- **Graph engine**: `rdflib` (in-memory `Graph`, SPARQL 1.1)
- **Package manager**: `uv`
- **Linter/formatter**: `ruff`
- **Type checker**: `mypy`
- **Test runner**: `pytest` + `pytest-asyncio`

---

## Repository Layout

```
data/
  knowledge_graph.ttl   # The fake knowledge graph (Turtle/RDF)

src/kg_mcp_server/
  server.py             # Entry point; imports & re-exports all tools and resources
  mcp_instance.py        # Shared FastMCP singleton (import this to register tools)
  server_setup.py        # Transport selection & server startup logic
  config.py               # Config dataclass + singleton loaded from env vars
  auth.py                 # Optional OAuth 2.0 provider for HTTP transport
  graph/
    store.py              # Loads the Turtle file, exposes run_select_query()
  tools/
    schema.py             # get_graph_schema, get_graph_stats
    accounts.py            # list_accounts, search_accounts, get_account
    contacts.py             # list_contacts_for_account, search_contacts, get_contact
    sparql.py                # run_sparql_query (raw read-only SPARQL)
  resources/
    guide.py                 # kg://guide MCP resource — usage guide for LLMs
  utils/
    validation.py             # SPARQL literal escaping, identifier normalization
    formatting.py              # Turns SPARQL result rows into readable text

tests/
  test_graph_store.py          # Graph loading + run_select_query tests
  test_accounts.py               # Account tool tests
  test_contacts.py                # Contact tool tests
  test_server.py                   # Import/registration smoke tests
```

---

## Development Environment

```bash
uv venv --python 3.12
source .venv/bin/activate   # Windows: .venv\Scripts\activate
uv sync --all-extras
```

### Environment Variables

| Variable | Required | Description |
|---|---|---|
| `KG_GRAPH_PATH` | No | Path to the Turtle file. Defaults to bundled `data/knowledge_graph.ttl`. |
| `KG_GRAPH_FORMAT` | No | RDF serialization format. Defaults to `turtle`. |
| `MCP_TRANSPORT` | No | `stdio` (default), `sse`, `http`, or `streamable-http`. |
| `FASTMCP_HOST` | No | Bind host for HTTP transport (default `127.0.0.1`; use `0.0.0.0` in Docker/Render). |
| `PORT` / `FASTMCP_PORT` | No | Bind port for HTTP transport (default `8000`). `PORT` takes priority (set automatically by Render); `FASTMCP_PORT` is a manual override. |
| `MCP_CLIENT_ID` / `MCP_CLIENT_SECRET` / `MCP_SERVER_URL` | No | Enable OAuth 2.0 (authorization code + PKCE) protection on the HTTP endpoint. |

---

## Running the Server

```bash
mcp run src/kg_mcp_server/server.py         # stdio transport (development)
python src/kg_mcp_server/server.py          # direct
```

### Docker

```bash
docker build -t kg-mcp-server .
docker run -e MCP_TRANSPORT=http -e FASTMCP_HOST=0.0.0.0 -p 8000:8000 kg-mcp-server
```

---

## Code Quality — Required Before Every Commit

```bash
ruff check .
ruff format .
mypy src tests
pytest
```

---

## Key Architectural Patterns

### Read-only knowledge graph

The graph is loaded once per process (`graph/store.get_graph()`, a
threading-safe singleton) and treated as **read-only**. `run_select_query()`
rejects any SPARQL containing `INSERT`/`DELETE`/`DROP`/`LOAD`/`CREATE` and
only accepts `SELECT`/`ASK` (optionally preceded by `PREFIX` declarations).

### Tool Registration

Tools register themselves via `@mcp.tool()` decorators when their module is
imported. Each tool module imports the shared `mcp` singleton from
`mcp_instance.py`:

```python
from kg_mcp_server.mcp_instance import mcp

@mcp.tool(annotations=ToolAnnotations(title="...", read_only_hint=True, destructive_hint=False))
async def my_tool(...) -> str:
    ...
```

`server.py` imports all tool modules to trigger registration, then re-exports
the functions in `__all__` for test compatibility.

### SPARQL query building

Tool modules build parameterized SPARQL query strings (see `tools/accounts.py`
and `tools/contacts.py`) and always escape user-supplied text via
`utils.validation.escape_sparql_literal()` before interpolating it into a
string literal or `FILTER(...)` clause.

### Configuration Singleton

```python
from kg_mcp_server.config import get_config

config = get_config()
```

---

## Adding a New MCP Tool

1. Create the function in the appropriate module under `src/kg_mcp_server/tools/`.
2. Decorate with `@mcp.tool(annotations=ToolAnnotations(...))`.
3. Build the SPARQL query, escaping any free-text input with
   `escape_sparql_literal()`, and execute it via
   `graph.store.run_select_query()`.
4. Return a formatted string (tools return `str`); reuse helpers in
   `utils/formatting.py` where possible.
5. Import and re-export the function in `server.py` (`__all__` list).
6. Write tests in `tests/` covering both matches and no-results cases.

---

## MCP Resource

The server exposes one MCP resource at `kg://guide` (registered in
`resources/guide.py`). It returns a plain-text usage guide describing the
Account/Contact domain and recommended tool call sequences. LLM clients
should load this resource at the start of a conversation.

## Operational Notes / Gotchas

### OAuth / HTTP transport
Activates only when `MCP_CLIENT_ID` + `MCP_CLIENT_SECRET` are set (`auth.py`,
`mcp_instance.py`). Gotchas: IDs/secret must match the connector exactly
(case-sensitive) and the connector URL must end in `/mcp`; `resource_server_url`
must be set (RFC 9728 metadata); the client must set
`token_endpoint_auth_method="client_secret_post"`.

### Render free tier cold starts
Free-tier services sleep after 15 minutes of inactivity; the first request
after sleeping can take 30-60 seconds while the graph reloads and the
container restarts.
