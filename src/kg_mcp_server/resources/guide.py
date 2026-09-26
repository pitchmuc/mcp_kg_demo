"""
Usage guide resource for the Knowledge Graph MCP server.

Provides a static plain-text briefing describing the fake CRM knowledge
graph domain (enterprise accounts + customer contacts) and recommended
tool workflows.
"""

from kg_mcp_server.mcp_instance import mcp

USAGE_GUIDE = """\
KNOWLEDGE GRAPH MCP SERVER — USAGE GUIDE

WHAT THIS IS

This server exposes a small, fictional CRM-style knowledge graph containing
enterprise customer Accounts and their Contacts (people). It is backed by a
Turtle (RDF) file queried with SPARQL via rdflib. All data is synthetic —
generated for demo/testing purposes and does not represent real companies.

CONCEPTS

Account — an enterprise customer organization. Has industry, tier, region,
  ARR, employee count, health score, renewal date, and an internal owner.

Contact — a person employed at an Account. Has a job title, a sales role
  (Economic Buyer / Champion / Influencer / User), contact details, whether
  they are considered an internal champion, and a sentiment rating.

Every Contact links to exactly one Account via crm:worksAt.

RECOMMENDED WORKFLOWS

Explore the graph:
  1. get_graph_schema()      ← see available classes/properties/namespace
  2. get_graph_stats()       ← quick triple/entity counts

Account research:
  1. list_accounts(tier=..., region=..., industry=..., min_health_score=...)
  2. get_account(account)    ← full detail + linked contacts in one call
  3. search_accounts(keyword)

Contact / relationship research:
  1. list_contacts_for_account(account, role=...)
  2. get_contact(contact)
  3. search_contacts(keyword, role=...)

Advanced / custom questions:
  1. get_graph_schema()      ← confirm property names first
  2. run_sparql_query(query) ← arbitrary read-only SELECT/ASK SPARQL

AVAILABLE TOOLS

  get_graph_schema           Describe classes, properties, and namespace.
  get_graph_stats            Basic triple/entity counts for the loaded graph.
  list_accounts              List/filter accounts by industry, tier, region, health score.
  search_accounts            Free-text search across accounts.
  get_account                Full detail for one account, plus its contacts.
  list_contacts_for_account  List contacts working at a given account.
  search_contacts            Free-text search across contacts.
  get_contact                Full detail for one contact.
  run_sparql_query           Arbitrary read-only SPARQL SELECT/ASK query.\
"""


@mcp.resource("kg://guide")
def usage_guide() -> str:
    """
    Usage guide for the Knowledge Graph MCP server. Describes the CRM-style
    account/contact domain and recommended tool workflows.
    """
    return USAGE_GUIDE
