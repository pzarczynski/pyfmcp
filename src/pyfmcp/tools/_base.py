"""Typed primitives shared by tool implementations."""

import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import msgspec
from fastmcp import FastMCP

from pyfmcp.schemas import ExecResult
from pyfmcp.schemas._base import BaseResult


class ToolOutputError(RuntimeError):
    """Raised when a tool emits output that cannot be decoded."""


def decode_json[T](raw: str, type_: type[T]) -> T:
    try:
        return msgspec.json.decode(raw, type=type_)
    except msgspec.DecodeError as exc:
        raise ToolOutputError(f"tool returned invalid JSON: {exc}") from exc


def run_cmd(command: list[str], timeout: float | None, cwd: Path) -> ExecResult:
    try:
        proc = subprocess.run(
            command, capture_output=True, text=True, timeout=timeout, cwd=cwd
        )
    except subprocess.TimeoutExpired as exc:
        raise ToolOutputError(f"tool timed out after {timeout} seconds") from exc
    return ExecResult(exit_code=proc.returncode, stdout=proc.stdout, stderr=proc.stderr)


class CommandRunner(Protocol):
    def __call__(
        self, command: list[str], timeout: float | None, cwd: Path
    ) -> ExecResult: ...


class ToolContext:
    """Shared project root and subprocess runner for tool adapters."""

    root: Path
    runner: CommandRunner

    def __init__(self, root: Path, runner: CommandRunner | None = None) -> None:
        self.root = root
        self.runner = run_cmd if runner is None else runner


class ToolSettings(msgspec.Struct, frozen=True):
    """Base class for validated per-tool runtime settings."""

    timeout: float | None = None


class ToolSpecProtocol(Protocol):
    @property
    def name(self) -> str: ...

    def register(
        self,
        mcp: FastMCP,
        context: ToolContext,
        settings_loader: Callable[[], object],
    ) -> None: ...


@dataclass(frozen=True, kw_only=True)
class ToolSpec[T: ToolSettings, R: BaseResult]:
    name: str
    settings_type: type[T]
    register_tool: Callable[[FastMCP, ToolContext, Callable[[], T]], None]

    def decode_settings(self, raw: object) -> T:
        try:
            return msgspec.convert(raw, type=self.settings_type)
        except (msgspec.DecodeError, TypeError, ValueError) as e:
            raise ValueError(f"invalid settings for tool {self.name!r}: {e}") from e

    def register(
        self,
        mcp: FastMCP,
        context: ToolContext,
        settings_loader: Callable[[], object],
    ) -> None:
        def load() -> T:
            return self.decode_settings(settings_loader())

        self.register_tool(mcp, context, load)


def make_tool_handler[S: ToolSettings, R: BaseResult](
    context: ToolContext,
    settings_loader: Callable[[], S],
    command: Callable[[S, tuple[str, ...]], list[str]],
    parser: Callable[[ExecResult, S], R],
) -> Callable[[tuple[str, ...]], R]:
    def run(paths: tuple[str, ...]) -> R:
        settings = settings_loader()
        result = context.runner(
            command(settings, paths), settings.timeout, context.root
        )
        return parser(result, settings)

    return run
