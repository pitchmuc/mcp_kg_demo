"""
Knowledge graph store for the Knowledge Graph MCP Server.

Loads the bundled (or configured) Turtle file into an in-memory RDFLib
graph once per process and exposes helpers for running read-only SPARQL
queries against it. The graph is intentionally treated as read-only:
this server is a query surface, not a writer.
"""

import logging
import threading
from pathlib import Path
from typing import Any

from rdflib import Graph, Namespace
from rdflib.query import ResultRow

from kg_mcp_server.config import get_config

logger = logging.getLogger("kg_mcp_server")

# The CRM ontology namespace used throughout the fake knowledge graph.
CRM = Namespace("http://example.org/crm#")

_graph: Graph | None = None
_lock = threading.Lock()


def _load_graph() -> Graph:
    config = get_config()
    graph_path = Path(config.graph_path)
    if not graph_path.is_file():
        raise FileNotFoundError(
            f"Knowledge graph file not found at '{graph_path}'. "
            "Set KG_GRAPH_PATH to point at a valid Turtle file."
        )

    graph = Graph()
    graph.parse(graph_path, format=config.graph_format)
    graph.bind("crm", CRM)
    logger.info("Loaded knowledge graph from %s (%d triples).", graph_path, len(graph))
    return graph


def get_graph() -> Graph:
    """
    Get the shared, lazily-loaded RDFLib graph instance (singleton pattern).

    Returns:
        Graph: The parsed knowledge graph.
    """
    global _graph  # pylint: disable=global-statement  # noqa: PLW0603 - singleton pattern
    if _graph is None:
        with _lock:
            if _graph is None:
                _graph = _load_graph()
    return _graph


def reload_graph() -> Graph:
    """Force a reload of the graph from disk. Mainly useful for tests."""
    global _graph  # pylint: disable=global-statement  # noqa: PLW0603 - singleton pattern
    with _lock:
        _graph = _load_graph()
    return _graph


def _coerce_value(value: Any) -> Any:
    """Convert an RDFLib term to a plain Python value for JSON-friendly output."""
    if value is None:
        return None
    to_python = getattr(value, "toPython", None)
    if callable(to_python):
        try:
            return to_python()
        except (TypeError, ValueError):
            pass
    return str(value)


def run_select_query(query: str) -> list[dict[str, Any]]:
    """
    Run a read-only SPARQL SELECT (or ASK) query against the knowledge graph.

    Args:
        query: The SPARQL query text.

    Returns:
        list[dict[str, Any]]: One dict per result row, keyed by variable name.

    Raises:
        ValueError: If the query is not a SELECT/ASK query, or fails to parse/execute.
    """
    normalized = query.strip().lstrip("#").strip()
    upper = normalized.upper()
    if not (upper.startswith("SELECT") or upper.startswith("ASK") or upper.startswith("PREFIX")):
        raise ValueError(
            "Only read-only SPARQL SELECT/ASK queries are supported "
            "(optionally preceded by PREFIX declarations)."
        )
    if any(keyword in upper for keyword in ("INSERT", "DELETE", "DROP", "CLEAR", "LOAD", "CREATE")):
        raise ValueError("Write operations are not permitted against this knowledge graph.")

    graph = get_graph()
    try:
        result = graph.query(normalized, initNs={"crm": CRM})
    except Exception as exc:  # pylint: disable=broad-except
        raise ValueError(f"Invalid SPARQL query: {exc}") from exc

    rows: list[dict[str, Any]] = []
    if result.type == "ASK":
        rows.append({"ask": bool(result.askAnswer)})  # type: ignore[attr-defined]
        return rows

    variables = [str(v) for v in (result.vars or [])]
    for binding in result:
        # SELECT results always yield ResultRow (or plain tuples for older
        # rdflib versions); ASK results were already returned above.
        if isinstance(binding, ResultRow):
            row = {var: _coerce_value(binding[var]) for var in variables}
        else:
            values = binding if isinstance(binding, tuple) else (binding,)
            row = {
                var: _coerce_value(value)
                for var, value in zip(variables, values, strict=False)  # type: ignore[arg-type]
            }
        rows.append(row)
    return rows
