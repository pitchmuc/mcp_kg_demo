"""
Knowledge graph schema/statistics MCP tool.
"""

from mcp.types import ToolAnnotations

from kg_mcp_server.graph.store import get_graph
from kg_mcp_server.mcp_instance import mcp

_SCHEMA_TEXT = """\
KNOWLEDGE GRAPH SCHEMA (namespace: crm: <http://example.org/crm#>)

Classes:
  crm:Account — an enterprise customer organization.
  crm:Contact — a person employed at an Account.

Account properties:
  crm:name            (string)  Company name
  crm:industry        (string)  Industry sector
  crm:tier            (string)  "Strategic" | "Enterprise" | "Mid-Market"
  crm:region          (string)  "NA" | "EMEA" | "APAC"
  crm:arrUsd          (integer) Annual recurring revenue, USD
  crm:employeeCount   (integer) Number of employees
  crm:healthScore     (integer) Account health score, 0-100
  crm:renewalDate     (date)    Next contract renewal date
  crm:accountOwner    (string)  Name of the internal account owner (CSM/AE)
  crm:website         (string)  Company website URL

Contact properties:
  crm:name              (string)  Full name
  crm:worksAt           (IRI)     Link to the crm:Account the contact works at
  crm:jobTitle           (string)  Job title
  crm:role              (string)  "Economic Buyer" | "Champion" | "Influencer" | "User"
  crm:email             (string)  Email address
  crm:phone             (string)  Phone number
  crm:isChampion        (boolean) Whether this contact is an internal champion
  crm:sentiment         (string)  "Positive" | "Neutral" | "Negative"
  crm:lastContactedDate (date)    Date of last recorded contact

Relationships:
  crm:Contact --crm:worksAt--> crm:Account   (many contacts per account)

Example SPARQL (for run_sparql_query):
  PREFIX crm: <http://example.org/crm#>
  SELECT ?name ?tier ?healthScore WHERE {
    ?a a crm:Account ; crm:name ?name ; crm:tier ?tier ; crm:healthScore ?healthScore .
    FILTER(?healthScore < 50)
  } ORDER BY ?healthScore
"""


@mcp.tool(
    annotations=ToolAnnotations(
        title="Get Graph Schema", read_only_hint=True, destructive_hint=False
    )
)
async def get_graph_schema() -> str:
    """Describe the knowledge graph's classes, properties, and namespace.

    Call this before writing a raw SPARQL query with run_sparql_query, or to
    understand what fields are available on accounts and contacts.
    """
    return _SCHEMA_TEXT


@mcp.tool(
    annotations=ToolAnnotations(
        title="Get Graph Stats", read_only_hint=True, destructive_hint=False
    )
)
async def get_graph_stats() -> str:
    """Return basic statistics about the loaded knowledge graph (triple/entity counts)."""
    graph = get_graph()
    accounts = len(
        list(
            graph.query(
                "PREFIX crm: <http://example.org/crm#> SELECT ?a WHERE { ?a a crm:Account }"
            )
        )
    )
    contacts = len(
        list(
            graph.query(
                "PREFIX crm: <http://example.org/crm#> SELECT ?c WHERE { ?c a crm:Contact }"
            )
        )
    )
    return (
        f"Knowledge graph statistics:\n"
        f"- Total triples: {len(graph)}\n"
        f"- Accounts: {accounts}\n"
        f"- Contacts: {contacts}\n"
    )
