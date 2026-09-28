"""
Configuration management for the Knowledge Graph MCP Server.

This module handles loading configuration from environment variables,
following the same singleton pattern used across the project's modules.
"""

import os
from dataclasses import dataclass
from importlib import resources
from pathlib import Path

# Try to load environment variables from a .env file if present.
try:
    from dotenv import load_dotenv

    _ = load_dotenv()
except ImportError:
    # python-dotenv not installed, proceed without it
    pass


def _default_graph_path() -> str:
    """
    Resolve the default location of the bundled Turtle file.

    A real (non-editable) `pip install .` — e.g. inside the Docker image
    deployed to Render — bundles `data/knowledge_graph.ttl` inside the
    installed package (see the `force-include` mapping in pyproject.toml), so
    check there first via `importlib.resources`. Fall back to the path
    relative to the repo root, which is what resolves correctly for local
    / editable-install development (`uv sync`, `mcp run ...`).
    """
    packaged = resources.files("kg_mcp_server") / "data" / "knowledge_graph.ttl"
    if packaged.is_file():
        return str(packaged)
    return str(Path(__file__).resolve().parent.parent.parent / "data" / "knowledge_graph.ttl")


# Default location of the Turtle file bundled with the repository.
_DEFAULT_GRAPH_PATH = _default_graph_path()


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
