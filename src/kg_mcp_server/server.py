"""
Knowledge Graph MCP Server

This module implements a Model Context Protocol (MCP) server that exposes a
fictional CRM-style knowledge graph — enterprise Accounts and customer
Contacts — for querying by Claude, ChatGPT, or other MCP-compatible clients.

The graph is a Turtle (RDF) file, loaded into an in-memory rdflib Graph and
queried via SPARQL. See data/knowledge_graph.ttl for the raw data and
resources/guide.py (kg://guide) for a description of the domain.

Usage:
    This server is designed to be run as a standalone script and exposes several
    MCP tools for use with Claude Desktop, ChatGPT, or other MCP-compatible clients.

    To run the server:
        $ python src/kg_mcp_server/server.py

    MCP tools provided:
        - get_graph_schema
        - get_graph_stats
        - list_accounts
        - search_accounts
        - get_account
        - list_contacts_for_account
        - search_contacts
        - get_contact
        - run_sparql_query

    See the README for more details on configuration and usage.
"""

import logging

from kg_mcp_server.config import get_config
from kg_mcp_server.mcp_instance import mcp
from kg_mcp_server.server_setup import setup_transport, start_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("kg_mcp_server")

# Get configuration instance
config = get_config()

# Import tool modules to register them (tools register themselves via @mcp.tool() decorators)
from kg_mcp_server.tools.schema import get_graph_schema, get_graph_stats  # noqa: E402
from kg_mcp_server.tools.accounts import get_account, list_accounts, search_accounts  # noqa: E402
from kg_mcp_server.tools.contacts import (  # noqa: E402
    get_contact,
    list_contacts_for_account,
    search_contacts,
)
from kg_mcp_server.tools.sparql import run_sparql_query  # noqa: E402

# Import resource modules to register them (resources register themselves via @mcp.resource() decorators)
from kg_mcp_server.resources.guide import usage_guide  # noqa: E402

__all__ = [
    "get_graph_schema",
    "get_graph_stats",
    "list_accounts",
    "search_accounts",
    "get_account",
    "list_contacts_for_account",
    "search_contacts",
    "get_contact",
    "run_sparql_query",
    "usage_guide",
]


# Run the server
if __name__ == "__main__":
    # Eagerly load the graph at startup so parse errors surface immediately
    # rather than on the first tool call.
    from kg_mcp_server.graph.store import get_graph

    get_graph()

    selected_transport = setup_transport()
    start_server(mcp, selected_transport)
