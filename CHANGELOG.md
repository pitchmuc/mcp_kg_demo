# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - Unreleased

### Added
- Initial release: MCP server exposing a fictional CRM knowledge graph
  (enterprise Accounts + customer Contacts) backed by a Turtle/RDF file
  and queried via SPARQL (rdflib).
- Tools: `get_graph_schema`, `get_graph_stats`, `list_accounts`,
  `search_accounts`, `get_account`, `list_contacts_for_account`,
  `search_contacts`, `get_contact`, `run_sparql_query`.
- `kg://guide` MCP resource describing the domain and recommended workflows.
- Docker + Render deployment support, with optional OAuth 2.0 protection
  for the HTTP transport.
