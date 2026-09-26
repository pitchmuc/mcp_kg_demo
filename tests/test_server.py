"""Smoke tests for server module imports, tool/resource registration."""

import pytest

from kg_mcp_server import server
from kg_mcp_server.tools.schema import get_graph_schema, get_graph_stats
from kg_mcp_server.tools.sparql import run_sparql_query


def test_server_exports_all_tools() -> None:
    for name in server.__all__:
        assert hasattr(server, name)


@pytest.mark.asyncio
async def test_get_graph_stats_reports_counts() -> None:
    result = await get_graph_stats()
    assert "Accounts: 8" in result
    assert "Contacts: 19" in result


@pytest.mark.asyncio
async def test_get_graph_schema_mentions_namespace() -> None:
    result = await get_graph_schema()
    assert "crm:" in result
    assert "crm:Account" in result
    assert "crm:Contact" in result


@pytest.mark.asyncio
async def test_run_sparql_query_select() -> None:
    result = await run_sparql_query(
        "PREFIX crm: <http://example.org/crm#> "
        "SELECT (COUNT(?a) AS ?count) WHERE { ?a a crm:Account }"
    )
    assert "count" in result


@pytest.mark.asyncio
async def test_run_sparql_query_rejects_writes() -> None:
    result = await run_sparql_query('INSERT DATA { <urn:x> <urn:y> "z" }')
    assert "Error running SPARQL query" in result


@pytest.mark.asyncio
async def test_run_sparql_query_empty() -> None:
    result = await run_sparql_query("   ")
    assert "non-empty SPARQL query" in result
