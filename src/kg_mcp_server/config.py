"""
Configuration management for the Knowledge Graph MCP Server.

This module handles loading configuration from environment variables,
following the same singleton pattern used across the project's modules.
"""

import os
from dataclasses import dataclass
from pathlib import Path

# Try to load environment variables from a .env file if present.
try:
    from dotenv import load_dotenv

    _ = load_dotenv()
except ImportError:
    # python-dotenv not installed, proceed without it
    pass

# Default location of the Turtle file bundled with the repository.
_DEFAULT_GRAPH_PATH = str(
    Path(__file__).resolve().parent.parent.parent / "data" / "knowledge_graph.ttl"
)


@dataclass
class Config:
    """Configuration settings for the Knowledge Graph MCP Server."""

    graph_path: str
    graph_format: str
    user_agent: str


_config_instance: Config | None = None  # pylint: disable=invalid-name


def load_config() -> Config:
    """
    Load configuration from environment variables.

    Returns:
        Config: Configuration instance with loaded values.
    """
    graph_path = os.getenv("KG_GRAPH_PATH") or _DEFAULT_GRAPH_PATH
    graph_format = os.getenv("KG_GRAPH_FORMAT") or "turtle"
    user_agent = "kg-mcp-server/1.0"

    return Config(
        graph_path=graph_path,
        graph_format=graph_format,
        user_agent=user_agent,
    )


def get_config() -> Config:
    """
    Get the configuration instance (singleton pattern).

    Returns:
        Config: The configuration instance.
    """
    global _config_instance  # pylint: disable=global-statement  # noqa: PLW0603 - singleton pattern
    if _config_instance is None:
        _config_instance = load_config()
    return _config_instance
