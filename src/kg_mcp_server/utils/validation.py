"""
Shared validation and query-building helpers for the Knowledge Graph MCP Server.
"""

import re

_SAFE_LOCAL_NAME_RE = re.compile(r"^[A-Za-z0-9_-]+$")


def escape_sparql_literal(value: str) -> str:
    """
    Escape a string so it can be safely embedded inside a SPARQL string literal.

    Args:
        value: The raw string to embed (e.g. inside FILTER(CONTAINS(...))).

    Returns:
        str: The escaped string, safe to place between double quotes in SPARQL.
    """
    return value.replace("\\", "\\\\").replace('"', '\\"')


def extract_local_name(identifier: str) -> str:
    """
    Normalize an identifier that may be a full URI, a CURIE (crm:acct-x), or a
    bare local name (acct-x) into just the local name fragment.

    Args:
        identifier: The raw identifier supplied by the caller.

    Returns:
        str: The bare local name (e.g. "acct-atlasforge").
    """
    identifier = identifier.strip()
    if "#" in identifier:
        identifier = identifier.rsplit("#", 1)[-1]
    elif ":" in identifier and not identifier.startswith("http"):
        identifier = identifier.split(":", 1)[-1]
    return identifier


def looks_like_local_name(identifier: str) -> bool:
    """Return True if the identifier looks like a bare local name (id), not free text."""
    return bool(_SAFE_LOCAL_NAME_RE.match(identifier))
