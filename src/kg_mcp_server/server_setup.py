"""
Server setup and initialization for the Knowledge Graph MCP Server.

This module handles transport configuration and server startup logic.
"""

import logging
import os
from enum import Enum

from mcp.server.mcpserver import MCPServer

from kg_mcp_server.mcp_instance import MCP_HOST

logger = logging.getLogger("kg_mcp_server")

# mcp>=2's run_streamable_http_async() defaults these itself; kept here as
# named constants (rather than inline literals below) since start_server also
# needs them to log the URL before run() blocks.
_DEFAULT_PORT = 8000
_DEFAULT_STREAMABLE_HTTP_PATH = "/mcp"


class TransportAliases(str, Enum):
    """Supported values for the MCP_TRANSPORT environment variable."""

    STDIO = "stdio"
    HTTP = "http"
    SSE = "sse"
    STREAMABLE_HTTP = "streamable-http"


def setup_transport() -> TransportAliases:
    """
    Setup and validate the MCP transport configuration.

    Reads MCP_TRANSPORT environment variable and validates it against
    supported transport types.

    Returns:
        TransportAliases: The selected transport type.

    Raises:
        ValueError: If the transport type is not supported.
    """
    transport_env = os.getenv("MCP_TRANSPORT", TransportAliases.STDIO.value).lower()
    try:
        transport_alias = TransportAliases(transport_env)
    except ValueError as exc:
        allowed = ", ".join(item.value for item in TransportAliases)
        raise ValueError(f"Unsupported MCP_TRANSPORT value. Use one of: {allowed}.") from exc

    # Map SSE and HTTP aliases to STREAMABLE_HTTP
    selected_transport = (
        TransportAliases.STREAMABLE_HTTP
        if transport_alias in (TransportAliases.HTTP, TransportAliases.SSE)
        else transport_alias
    )

    return selected_transport


def start_server(mcp_instance: MCPServer, transport: TransportAliases) -> None:
    """
    Start the MCP server with the specified transport.

    Args:
        mcp_instance (MCPServer): The MCPServer instance to start.
        transport (TransportAliases): The transport type to use.
    """
    if transport == TransportAliases.STDIO:
        logger.info("Starting MCP server with stdio transport.")
        mcp_instance.run()
    else:  # STREAMABLE_HTTP
        logger.info(
            "Starting MCP server with Streamable HTTP transport at http://%s:%s%s.",
            MCP_HOST,
            _DEFAULT_PORT,
            _DEFAULT_STREAMABLE_HTTP_PATH,
        )
        mcp_instance.run(
            transport="streamable-http",
            host=MCP_HOST,
            port=_DEFAULT_PORT,
            streamable_http_path=_DEFAULT_STREAMABLE_HTTP_PATH,
        )
