"""
Formatting helpers to turn SPARQL result rows into human-readable text for
MCP tool responses.
"""

from typing import Any

# Preferred key order for account rows, when present.
_ACCOUNT_FIELD_ORDER = [
    "name",
    "industry",
    "tier",
    "region",
    "arrUsd",
    "employeeCount",
    "healthScore",
    "renewalDate",
    "accountOwner",
    "website",
]

_CONTACT_FIELD_ORDER = [
    "name",
    "jobTitle",
    "role",
    "accountName",
    "email",
    "phone",
    "isChampion",
    "sentiment",
    "lastContactedDate",
]


def _format_row(row: dict[str, Any], field_order: list[str], id_key: str, id_value: str) -> str:
    lines = [f"- **{id_value}**"]
    seen = set()
    for key in field_order:
        if key in row and row[key] is not None:
            lines.append(f"  - {key}: {row[key]}")
            seen.add(key)
    for key, value in row.items():
        if key not in seen and key != id_key and value is not None:
            lines.append(f"  - {key}: {value}")
    return "\n".join(lines)


def format_accounts(rows: list[dict[str, Any]]) -> str:
    """Format a list of account result rows into a readable bullet list."""
    if not rows:
        return "No matching accounts found."
    blocks = []
    for row in rows:
        account_id = row.get("accountId", row.get("name", "unknown"))
        blocks.append(_format_row(row, _ACCOUNT_FIELD_ORDER, "accountId", str(account_id)))
    return f"Found {len(rows)} account(s):\n\n" + "\n\n".join(blocks)


def format_contacts(rows: list[dict[str, Any]]) -> str:
    """Format a list of contact result rows into a readable bullet list."""
    if not rows:
        return "No matching contacts found."
    blocks = []
    for row in rows:
        contact_id = row.get("contactId", row.get("name", "unknown"))
        blocks.append(_format_row(row, _CONTACT_FIELD_ORDER, "contactId", str(contact_id)))
    return f"Found {len(rows)} contact(s):\n\n" + "\n\n".join(blocks)


def format_sparql_rows(rows: list[dict[str, Any]]) -> str:
    """Format raw SPARQL result rows as a simple markdown table."""
    if not rows:
        return "Query returned no results."
    columns = list(rows[0].keys())
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    body_lines = [
        "| " + " | ".join(str(row.get(col, "")) for col in columns) + " |" for row in rows
    ]
    return "\n".join([header, separator, *body_lines])
