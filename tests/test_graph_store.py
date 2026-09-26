"""Tests for the graph store loading and SPARQL query helpers."""

import pytest

from kg_mcp_server.graph.store import get_graph, run_select_query


def test_get_graph_loads_expected_triple_count() -> None:
    graph = get_graph()
    assert len(graph) > 0


def test_run_select_query_returns_accounts() -> None:
    rows = run_select_query(
        "PREFIX crm: <http://example.org/crm#> "
        "SELECT ?name WHERE { ?a a crm:Account ; crm:name ?name . } ORDER BY ?name"
    )
    names = {row["name"] for row in rows}
    assert "AtlasForge Manufacturing" in names
    assert len(rows) == 8


def test_run_select_query_rejects_write_operations() -> None:
    with pytest.raises(ValueError):
        run_select_query(
            'PREFIX crm: <http://example.org/crm#> INSERT DATA { crm:acct-fake crm:name "Fake" }'
        )


def test_run_select_query_rejects_invalid_query() -> None:
    with pytest.raises(ValueError):
        run_select_query("not a real sparql query")


def test_run_select_query_supports_ask() -> None:
    rows = run_select_query(
        "PREFIX crm: <http://example.org/crm#> "
        'ASK { ?a a crm:Account ; crm:name "AtlasForge Manufacturing" }'
    )
    assert rows == [{"ask": True}]
