# Knowledge Graph MCP Server

Model Context Protocol (MCP) server that exposes a **fictional CRM knowledge
graph** — enterprise **Accounts** and customer **Contacts** — for querying
from Claude, ChatGPT, Adobe Coworker, or any other MCP-compatible client.

The graph is a plain **Turtle/RDF file** (`data/knowledge_graph.ttl`), loaded
into memory with [rdflib](https://rdflib.readthedocs.io/) and queried via
**SPARQL**. All data is synthetic/made-up — it does not represent any real
company or person.

> This server mirrors the deployment setup used by the sibling
> `intervals-mcp-server` project (Docker + Render + optional OAuth), swapping
> a REST API integration for a self-contained knowledge graph.

## What's in the graph?

- **8 fictional enterprise accounts** across industries (manufacturing,
  financial services, software, retail, healthcare, logistics, energy,
  education), each with tier, region, ARR, employee count, health score,
  renewal date, and account owner.
- **19 fictional contacts** linked to those accounts, each with a job title,
  sales role (Economic Buyer / Champion / Influencer / User), email, phone,
  champion flag, sentiment, and last-contacted date.

See `src/kg_mcp_server/tools/schema.py` (`get_graph_schema` tool) for the
full property list and namespace.

## Setup — Deploy to Render (recommended)

The fastest way to get started is to deploy the server to
[Render](https://render.com) as a Docker Web Service. No local installation
required.

### 1. Create a Web Service on Render

1. Push this folder to its own GitHub repository.
2. Go to [render.com](https://render.com) → **New** → **Web Service** (or use
   the included `render.yaml` with **New → Blueprint**).
3. Connect your GitHub repository.
4. Configure the service:
   - **Name**: `kg-mcp-server` (or your preferred name)
   - **Runtime**: **Docker**
   - **Instance Type**: Free tier works fine

> **💤 Free tier cold starts:** Render free-tier services sleep after 15
> minutes of inactivity. The first request after sleeping may take 30-60
> seconds while the container restarts and the graph reloads. Subsequent
> requests are fast.

### 2. Set Environment Variables

In the Render dashboard under **Environment**, add:

| Key | Value | Description |
|-----|-------|-------------|
| `MCP_TRANSPORT` | `http` | Enables the remote transport (streamable HTTP) |
| `FASTMCP_HOST` | `0.0.0.0` | Bind to all interfaces (required inside Docker) |

Optional — enable OAuth 2.0 to protect the endpoint:

| Key | Value | Description |
|-----|-------|-------------|
| `MCP_CLIENT_ID` | `kg-mcp` | OAuth client ID; must match the connector config **exactly** |
| `MCP_CLIENT_SECRET` | `<random secret>` | OAuth client secret / access token; must match the connector |
| `MCP_SERVER_URL` | `https://your-service-name.onrender.com` | Public HTTPS URL (no `/mcp`); required for OAuth discovery |

### 3. Deploy and Verify

1. Click **Create Web Service** — Render will build the Docker image and deploy
2. Wait for the build to complete (green status)
3. Note your service URL: `https://your-service-name.onrender.com`
4. Test by opening `https://your-service-name.onrender.com/mcp` in a browser — you should get a response from the server

> **⚠️ Security Warning:** Without OAuth, your Render endpoint is publicly
> accessible — anyone who discovers the URL can query the knowledge graph
> (read-only; there is no write/mutate capability). Either enable OAuth or
> do not share your service URL publicly.

## Connecting Claude

1. Open Claude → **Settings** → **Integrations** (or **MCP Servers**)
2. Click **Add**
3. Fill in:
   - **Name:** `Knowledge Graph`
   - **URL:** `https://your-service-name.onrender.com/mcp` (must end with `/mcp`)
   - If OAuth is enabled, also set **OAuth Client ID** / **OAuth Client Secret**

Open a new conversation and ask "What MCP tools do you have available?" to confirm the connection.

## Connecting ChatGPT / Adobe Coworker / other MCP clients

Any MCP-compatible client that supports remote (Streamable HTTP) servers can
connect the same way:

- **MCP Server URL**: `https://your-service-name.onrender.com/mcp`
- OAuth Client ID / Secret if enabled

## Available Tools

- `get_graph_schema` — describe the graph's classes, properties, and namespace
- `get_graph_stats` — triple/entity counts for the loaded graph
- `list_accounts` — list/filter accounts by industry, tier, region, health score
- `search_accounts` — free-text search across accounts
- `get_account` — full detail for one account, including its contacts
- `list_contacts_for_account` — list contacts working at a given account
- `search_contacts` — free-text search across contacts
- `get_contact` — full detail for one contact
- `run_sparql_query` — arbitrary read-only SPARQL `SELECT`/`ASK` query

There is also an MCP resource, `kg://guide`, with a usage guide LLM clients
can load at the start of a conversation.

## Troubleshooting Render Deployment

- **Service won't start** — Check Render logs for build errors.
- **Claude/ChatGPT can't connect** — Verify the URL ends with `/mcp` and is publicly accessible. Try opening it in a browser.
- **"Authorization failed" with OAuth** — `MCP_CLIENT_ID`/`MCP_CLIENT_SECRET` must match the connector exactly (case-sensitive), `MCP_SERVER_URL` must be the public HTTPS URL without `/mcp`, and the connector URL must end with `/mcp`.
- **Free tier cold starts** — first request after sleeping may take 30-60 seconds.

---

<details>
<summary><strong>Local Setup (alternative)</strong></summary>

### Requirements

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) (recommended package manager)

### 1. Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone and install

```bash
cd kg_mcp_server
uv venv --python 3.12
source .venv/bin/activate   # Windows: .venv\Scripts\activate
uv sync --all-extras
```

### Configure Claude Desktop (stdio)

```bash
mcp install src/kg_mcp_server/server.py --name "Knowledge Graph"
```

Or manually add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "Knowledge Graph": {
      "command": "uv",
      "args": [
        "run", "--with", "mcp[cli]",
        "--with-editable", "/path/to/kg_mcp_server",
        "mcp", "run", "/path/to/kg_mcp_server/src/kg_mcp_server/server.py"
      ]
    }
  }
}
```

### Running over HTTP locally (for ChatGPT / remote testing)

```bash
export FASTMCP_HOST=127.0.0.1 FASTMCP_PORT=8000 MCP_TRANSPORT=http
python src/kg_mcp_server/server.py
```

Forward the port with a tunnel (e.g. `ngrok http 8000`) to give a remote
client a public URL.

### Editing the knowledge graph

Edit `data/knowledge_graph.ttl` directly — it's plain Turtle. Restart the
server (or call `kg_mcp_server.graph.store.reload_graph()`) to pick up
changes. Use `KG_GRAPH_PATH` to point at a different file entirely.

</details>

## Development and testing

```bash
uv sync --all-extras
ruff check .
mypy src tests
pytest -v tests
```

## License

The GNU General Public License v3.0
