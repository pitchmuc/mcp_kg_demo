"""
Raw SPARQL query MCP tool backed by the knowledge graph.
"""

from mcp.types import ToolAnnotations

from kg_mcp_server.graph.store import run_select_query
from kg_mcp_server.mcp_instance import mcp
from kg_mcp_server.utils.formatting import format_sparql_rows


@mcp.tool(
    annotations=ToolAnnotations(
        title="Run SPARQL Query", read_only_hint=True, destructive_hint=False
    )
)
async def run_sparql_query(query: str) -> str:
    """Run a read-only SPARQL SELECT or ASK query directly against the knowledge graph.

    Use this for questions the higher-level account/contact tools can't answer,
    e.g. joins, aggregations, or custom filters. The graph uses the `crm:`
    prefix (http://example.org/crm#) for all classes and properties — call
    get_graph_schema() first to see available classes and properties.

    Only SELECT and ASK queries are permitted; INSERT/DELETE/DROP/LOAD/CREATE
    are rejected. `PREFIX crm: <http://example.org/crm#>` is available
    automatically but may also be declared explicitly.

    Args:
        query: The SPARQL query text, e.g.
            "SELECT ?name ?arrUsd WHERE { ?a a crm:Account ; crm:name ?name ;
            crm:arrUsd ?arrUsd . } ORDER BY DESC(?arrUsd) LIMIT 5"
    """
    if not query.strip():
        return "Please provide a non-empty SPARQL query."
    try:
        rows = run_select_query(query)
    except ValueError as exc:
        return f"Error running SPARQL query: {exc}"
    return format_sparql_rows(rows)
