from collections.abc import Mapping

from fastmcp import FastMCP

from pyfmcp.config import Config

from ._base import ToolContext, ToolSpecProtocol
from ._basedpyright import BASEDPYRIGHT_SPEC
from ._pytest import PYTEST_SPEC
from ._ruff import RUFF_SPEC
from ._settings import load_settings

SPECS: Mapping[str, ToolSpecProtocol] = {
    "basedpyright": BASEDPYRIGHT_SPEC,
    "pytest": PYTEST_SPEC,
    "ruff": RUFF_SPEC,
}


def register_tools(mcp: FastMCP, context: ToolContext, config: Config) -> None:
    """Register the tools selected by process configuration."""
    names = tuple(SPECS) if config.tools is None else config.tools
    unknown = tuple(name for name in names if name not in SPECS)
    if unknown:
        raise ValueError(f"unknown configured tool name(s): {', '.join(unknown)}")

    def settings_for(name: str) -> object:
        settings = load_settings(config)
        return settings.tools.get(name, {})

    for name in names:
        SPECS[name].register(mcp, context, lambda name=name: settings_for(name))


__all__ = ["SPECS", "register_tools"]
