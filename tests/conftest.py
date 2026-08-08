from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import msgspec
import pytest
from fastmcp import Client, FastMCP

from pyfmcp.config import Config
from pyfmcp.schemas import ExecResult
from pyfmcp.tools import register_tools
from pyfmcp.tools._base import ToolContext, ToolSettings
from pyfmcp.tools._settings import RuntimeSettings


def write_tool_settings(
    path: Path, tool_settings: ToolSettings, tool_name: str
) -> None:
    settings = RuntimeSettings(tools={tool_name: tool_settings})
    path.write_bytes(msgspec.yaml.encode(settings))


@dataclass(frozen=True)
class CommandCall:
    command: list[str]
    timeout: float | None
    cwd: Path


class CommandRecorder:
    def __init__(self) -> None:
        self.calls: list[CommandCall] = []
        self._results: list[ExecResult] = []
        self.junit_report: str | None = None

    def add_result(self, result: ExecResult) -> None:
        self._results.append(result)

    def __call__(
        self, command: list[str], timeout: float | None, cwd: Path
    ) -> ExecResult:
        self.calls.append(CommandCall(command, timeout, cwd))
        if self.junit_report is not None:
            report = next(
                argument for argument in command if argument.startswith("--junitxml=")
            )
            Path(report.split("=", 1)[1]).write_text(self.junit_report)
        if not self._results:
            raise AssertionError("no scripted command result")
        return self._results.pop(0)


@pytest.fixture
def command_runner(monkeypatch: pytest.MonkeyPatch) -> CommandRecorder:
    recorder = CommandRecorder()
    monkeypatch.setattr("pyfmcp.tools._base.run_cmd", recorder)
    return recorder


@pytest.fixture
def make_mcp(
    command_runner: CommandRecorder,
) -> Callable[[Path, Config], FastMCP]:
    def _make(root: Path, config: Config) -> FastMCP:
        mcp = FastMCP("pyfmcp")
        register_tools(mcp, ToolContext(root=root, runner=command_runner), config)
        return mcp

    return _make


@pytest.mark.asyncio
async def invoke_tool(
    server: FastMCP, name: str, arguments: dict[str, object] | None = None
) -> object:
    async with Client(server) as client:
        result = await client.call_tool(name, arguments or {})
        attributes: dict[str, object] = vars(result)
        return attributes["data"]


@pytest.mark.asyncio
async def list_tool_names(server: FastMCP) -> set[str]:
    async with Client(server) as client:
        tools = await client.list_tools()
        return {tool.name for tool in tools}
