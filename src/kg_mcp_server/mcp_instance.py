"""
Shared MCP instance module.

Provides a shared MCPServer instance importable by both the server module
and tool modules without creating cyclic imports, mirroring the pattern
used across sibling MCP server projects in this workspace.
"""

import logging
import os

from pydantic import AnyHttpUrl

from mcp.server.mcpserver import MCPServer

logger = logging.getLogger("kg_mcp_server")

_mcp_client_id = os.getenv("MCP_CLIENT_ID", "")
_mcp_client_secret = os.getenv("MCP_CLIENT_SECRET", "")
_mcp_server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000")

# mcp>=2 moved host/port off the MCPServer constructor and onto run() (see
# server_setup.start_server), so the FASTMCP_HOST env var is captured here
# as a module-level constant instead of passed to MCPServer() below.
MCP_HOST = os.getenv("FASTMCP_HOST", "127.0.0.1")

_auth_server_provider = None
_auth_settings = None

if _mcp_client_id and _mcp_client_secret:
    from mcp.server.auth.settings import AuthSettings

    from kg_mcp_server.auth import SingleClientOAuthProvider

    _auth_server_provider = SingleClientOAuthProvider(_mcp_client_id, _mcp_client_secret)
    # This server is both the authorization server and the resource server.
    # issuer_url            -> publishes /.well-known/oauth-authorization-server (AS metadata)
    # resource_server_url   -> publishes /.well-known/oauth-protected-resource (RFC 9728)
    #                          and adds the resource_metadata pointer to the 401
    #                          WWW-Authenticate header. Claude.ai's connector flow
    #                          requires this protected-resource metadata to authorize.
    _server_url = AnyHttpUrl(_mcp_server_url)
    _auth_settings = AuthSettings(
        issuer_url=_server_url,
        resource_server_url=_server_url,
    )
    logger.info("OAuth authentication enabled for HTTP transport.")
else:
    logger.debug("MCP_CLIENT_ID/MCP_CLIENT_SECRET not set; HTTP endpoint is unauthenticated.")

mcp: MCPServer = MCPServer(
    "knowledge-graph",
    auth_server_provider=_auth_server_provider,  # type: ignore[arg-type]
    auth=_auth_settings,
)
