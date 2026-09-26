"""
Contact (customer people) MCP tools backed by the knowledge graph.
"""

from mcp.types import ToolAnnotations

from kg_mcp_server.graph.store import run_select_query
from kg_mcp_server.mcp_instance import mcp
from kg_mcp_server.utils.formatting import format_contacts
from kg_mcp_server.utils.validation import escape_sparql_literal, extract_local_name

_CONTACT_SELECT = """
PREFIX crm: <http://example.org/crm#>
SELECT ?contactId ?name ?jobTitle ?role ?accountName ?email ?phone
       ?isChampion ?sentiment ?lastContactedDate
WHERE {{
  ?contact a crm:Contact ;
           crm:name ?name ;
           crm:worksAt ?account .
  ?account crm:name ?accountName .
  BIND(STRAFTER(STR(?contact), "#") AS ?contactId)
  OPTIONAL {{ ?contact crm:jobTitle ?jobTitle }}
  OPTIONAL {{ ?contact crm:role ?role }}
  OPTIONAL {{ ?contact crm:email ?email }}
  OPTIONAL {{ ?contact crm:phone ?phone }}
  OPTIONAL {{ ?contact crm:isChampion ?isChampion }}
  OPTIONAL {{ ?contact crm:sentiment ?sentiment }}
  OPTIONAL {{ ?contact crm:lastContactedDate ?lastContactedDate }}
  {filters}
}}
ORDER BY ?name
"""


@mcp.tool(
    annotations=ToolAnnotations(
        title="List Contacts For Account", read_only_hint=True, destructive_hint=False
    )
)
async def list_contacts_for_account(account: str, role: str = "") -> str:
    """List contacts (people) who work at a given account.

    Args:
        account: The account identifier (e.g. "acct-atlasforge") or a name/substring
            (e.g. "AtlasForge").
        role: Optional exact match on contact role, e.g. "Economic Buyer",
            "Champion", "Influencer", "User".
    """
    if not account.strip():
        return "Please provide an account identifier or name."

    local_name = extract_local_name(account)
    safe_id = escape_sparql_literal(local_name)
    safe_text = escape_sparql_literal(account.strip())
    filters = [
        f'FILTER(STRAFTER(STR(?account), "#") = "{safe_id}" || '
        f'CONTAINS(LCASE(?accountName), LCASE("{safe_text}")))'
    ]
    if role:
        safe_role = escape_sparql_literal(role)
        filters.append(f'FILTER(?role = "{safe_role}")')

    query = _CONTACT_SELECT.format(filters="\n  ".join(filters))
    try:
        rows = run_select_query(query)
    except ValueError as exc:
        return f"Error listing contacts: {exc}"
    return format_contacts(rows)


@mcp.tool(
    annotations=ToolAnnotations(
        title="Search Contacts", read_only_hint=True, destructive_hint=False
    )
)
async def search_contacts(keyword: str, role: str = "") -> str:
    """Search contacts by keyword matched against name, job title, or account name.

    Args:
        keyword: Free-text keyword to search for (case-insensitive substring match).
        role: Optional exact match on contact role, e.g. "Economic Buyer",
            "Champion", "Influencer", "User".
    """
    if not keyword.strip():
        return "Please provide a non-empty keyword to search for."
    safe = escape_sparql_literal(keyword)
    filters = [
        f'FILTER(CONTAINS(LCASE(?name), LCASE("{safe}")) || '
        f'CONTAINS(LCASE(COALESCE(?jobTitle, "")), LCASE("{safe}")) || '
        f'CONTAINS(LCASE(?accountName), LCASE("{safe}")))'
    ]
    if role:
        safe_role = escape_sparql_literal(role)
        filters.append(f'FILTER(?role = "{safe_role}")')

    query = _CONTACT_SELECT.format(filters="\n  ".join(filters))
    try:
        rows = run_select_query(query)
    except ValueError as exc:
        return f"Error searching contacts: {exc}"
    return format_contacts(rows)


@mcp.tool(
    annotations=ToolAnnotations(title="Get Contact", read_only_hint=True, destructive_hint=False)
)
async def get_contact(contact: str) -> str:
    """Get full details for a single contact.

    Args:
        contact: The contact identifier (e.g. "contact-adriana-koll"), or a
            name/substring to look up (e.g. "Adriana Koll" or "koll").
    """
    if not contact.strip():
        return "Please provide a contact identifier or name."

    local_name = extract_local_name(contact)
    safe_id = escape_sparql_literal(local_name)
    safe_text = escape_sparql_literal(contact.strip())
    filters = [f'FILTER(?contactId = "{safe_id}" || CONTAINS(LCASE(?name), LCASE("{safe_text}")))']
    query = _CONTACT_SELECT.format(filters="\n  ".join(filters))
    try:
        rows = run_select_query(query)
    except ValueError as exc:
        return f"Error fetching contact: {exc}"

    if not rows:
        return f"No contact found matching '{contact}'."
    if len(rows) > 1:
        names = ", ".join(f"{r['name']} ({r['contactId']})" for r in rows)
        return f"Multiple contacts match '{contact}': {names}. Please be more specific."
    return format_contacts(rows)
