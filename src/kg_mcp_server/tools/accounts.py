"""
Account (enterprise customer) MCP tools backed by the knowledge graph.
"""

from mcp.types import ToolAnnotations

from kg_mcp_server.graph.store import run_select_query
from kg_mcp_server.mcp_instance import mcp
from kg_mcp_server.utils.formatting import format_accounts, format_contacts
from kg_mcp_server.utils.validation import escape_sparql_literal, extract_local_name

_ACCOUNT_SELECT = """
PREFIX crm: <http://example.org/crm#>
SELECT ?accountId ?name ?industry ?tier ?region ?arrUsd ?employeeCount
       ?healthScore ?renewalDate ?accountOwner ?website
WHERE {{
  ?account a crm:Account ;
           crm:name ?name .
  BIND(STRAFTER(STR(?account), "#") AS ?accountId)
  OPTIONAL {{ ?account crm:industry ?industry }}
  OPTIONAL {{ ?account crm:tier ?tier }}
  OPTIONAL {{ ?account crm:region ?region }}
  OPTIONAL {{ ?account crm:arrUsd ?arrUsd }}
  OPTIONAL {{ ?account crm:employeeCount ?employeeCount }}
  OPTIONAL {{ ?account crm:healthScore ?healthScore }}
  OPTIONAL {{ ?account crm:renewalDate ?renewalDate }}
  OPTIONAL {{ ?account crm:accountOwner ?accountOwner }}
  OPTIONAL {{ ?account crm:website ?website }}
  {filters}
}}
ORDER BY ?name
"""


@mcp.tool(
    annotations=ToolAnnotations(title="List Accounts", read_only_hint=True, destructive_hint=False)
)
async def list_accounts(
    industry: str = "",
    tier: str = "",
    region: str = "",
    min_health_score: int = 0,
) -> str:
    """List enterprise accounts in the knowledge graph, optionally filtered.

    Args:
        industry: Case-insensitive substring match on industry (optional).
        tier: Exact match on account tier, e.g. "Strategic", "Enterprise",
            "Mid-Market" (optional).
        region: Exact match on region code, e.g. "NA", "EMEA", "APAC" (optional).
        min_health_score: Only return accounts with healthScore >= this value
            (optional, defaults to 0 i.e. no filtering).
    """
    filters = []
    if industry:
        safe = escape_sparql_literal(industry)
        filters.append(f'FILTER(CONTAINS(LCASE(?industry), LCASE("{safe}")))')
    if tier:
        safe = escape_sparql_literal(tier)
        filters.append(f'FILTER(?tier = "{safe}")')
    if region:
        safe = escape_sparql_literal(region)
        filters.append(f'FILTER(?region = "{safe}")')
    if min_health_score:
        filters.append(f"FILTER(?healthScore >= {int(min_health_score)})")

    query = _ACCOUNT_SELECT.format(filters="\n  ".join(filters))
    try:
        rows = run_select_query(query)
    except ValueError as exc:
        return f"Error listing accounts: {exc}"
    return format_accounts(rows)


@mcp.tool(
    annotations=ToolAnnotations(
        title="Search Accounts", read_only_hint=True, destructive_hint=False
    )
)
async def search_accounts(keyword: str) -> str:
    """Search accounts by a keyword matched against name, industry, or account owner.

    Args:
        keyword: Free-text keyword to search for (case-insensitive substring match).
    """
    if not keyword.strip():
        return "Please provide a non-empty keyword to search for."
    safe = escape_sparql_literal(keyword)
    filters = (
        f'FILTER(CONTAINS(LCASE(?name), LCASE("{safe}")) || '
        f'CONTAINS(LCASE(COALESCE(?industry, "")), LCASE("{safe}")) || '
        f'CONTAINS(LCASE(COALESCE(?accountOwner, "")), LCASE("{safe}")))'
    )
    query = _ACCOUNT_SELECT.format(filters=filters)
    try:
        rows = run_select_query(query)
    except ValueError as exc:
        return f"Error searching accounts: {exc}"
    return format_accounts(rows)


@mcp.tool(
    annotations=ToolAnnotations(title="Get Account", read_only_hint=True, destructive_hint=False)
)
async def get_account(account: str, include_contacts: bool = True) -> str:
    """Get full details for a single account, including its contacts.

    Args:
        account: The account identifier (e.g. "acct-atlasforge"), or a
            name/substring to look up (e.g. "AtlasForge" or "atlasforge manufacturing").
        include_contacts: Whether to also list contacts linked to this account
            (optional, defaults to True).
    """
    if not account.strip():
        return "Please provide an account identifier or name."

    local_name = extract_local_name(account)
    safe_id = escape_sparql_literal(local_name)
    safe_text = escape_sparql_literal(account.strip())
    filters = f'FILTER(?accountId = "{safe_id}" || CONTAINS(LCASE(?name), LCASE("{safe_text}")))'
    query = _ACCOUNT_SELECT.format(filters=filters)
    try:
        rows = run_select_query(query)
    except ValueError as exc:
        return f"Error fetching account: {exc}"

    if not rows:
        return f"No account found matching '{account}'."
    if len(rows) > 1:
        names = ", ".join(f"{r['name']} ({r['accountId']})" for r in rows)
        return f"Multiple accounts match '{account}': {names}. Please be more specific."

    result = format_accounts(rows)
    if include_contacts:
        account_id = rows[0]["accountId"]
        contacts = await _contacts_for_account_id(account_id)
        result += "\n\nContacts:\n\n" + contacts
    return result


async def _contacts_for_account_id(account_id: str) -> str:
    """Internal helper shared with tools.contacts to list contacts for an account id."""
    safe_id = escape_sparql_literal(account_id)
    query = f"""
PREFIX crm: <http://example.org/crm#>
SELECT ?contactId ?name ?jobTitle ?role ?email ?phone ?isChampion ?sentiment ?lastContactedDate
WHERE {{
  ?contact a crm:Contact ;
           crm:name ?name ;
           crm:worksAt ?account .
  BIND(STRAFTER(STR(?contact), "#") AS ?contactId)
  FILTER(STRAFTER(STR(?account), "#") = "{safe_id}")
  OPTIONAL {{ ?contact crm:jobTitle ?jobTitle }}
  OPTIONAL {{ ?contact crm:role ?role }}
  OPTIONAL {{ ?contact crm:email ?email }}
  OPTIONAL {{ ?contact crm:phone ?phone }}
  OPTIONAL {{ ?contact crm:isChampion ?isChampion }}
  OPTIONAL {{ ?contact crm:sentiment ?sentiment }}
  OPTIONAL {{ ?contact crm:lastContactedDate ?lastContactedDate }}
}}
ORDER BY ?name
"""
    rows = run_select_query(query)
    return format_contacts(rows)
