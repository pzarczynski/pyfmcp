from pathlib import Path

from fastmcp import FastMCP

from .config import Config
from .tools import register_tools
from .tools._base import ToolContext


def create_mcp(root: Path, cfg: Config | None = None) -> FastMCP:
    """Create an MCP server rooted at ``root`` with the selected tools."""
    config = cfg if cfg is not None else Config(root_dir=root)
    context = ToolContext(root=root)
    mcp = FastMCP(
        "pyfmcp",
        instructions=(
            "Run the project's configured pytest, Ruff, and basedpyright tools. "
            "Tool selection is configured by the application configuration; "
            "runtime tool settings are reloaded for each invocation."
        ),
    )
    register_tools(mcp, context, config)
    return mcp
