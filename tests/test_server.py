"""MCP integration tests for server registration and runtime configuration."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest
from fastmcp import FastMCP

from pyfmcp.config import Config
from pyfmcp.tools import register_tools
from pyfmcp.tools._base import ToolContext

from .conftest import list_tool_names


@pytest.mark.asyncio
async def test_explicit_tool_selection_registers_only_requested(
    tmp_path: Path,
    make_mcp: Callable[[Path, Config], FastMCP],
) -> None:
    config = Config(root_dir=tmp_path, tools=("ruff",))

    assert await list_tool_names(make_mcp(tmp_path, config)) == {"ruff_lint"}


def test_unknown_configured_tool_name_raises(tmp_path: Path) -> None:
    config = Config(root_dir=tmp_path, tools=("pytest", "bogus"))

    with pytest.raises(ValueError, match="bogus"):
        register_tools(FastMCP("pyfmcp"), ToolContext(root=tmp_path), config)
