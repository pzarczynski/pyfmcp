from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import cast

import pytest
from fastmcp import FastMCP

from pyfmcp.config import Config
from pyfmcp.schemas import ExecResult
from pyfmcp.schemas._basedpyright import BPResult
from pyfmcp.schemas._pytest import PytestResult, parse_pytest_junit
from pyfmcp.schemas._ruff import RuffResult
from pyfmcp.tools._basedpyright import BasedpyrightSettings
from pyfmcp.tools._pytest import PytestSettings
from pyfmcp.tools._ruff import RuffSettings

from .conftest import CommandRecorder, invoke_tool, write_tool_settings


@pytest.mark.asyncio
async def test_ruff_invoke(
    tmp_path: Path,
    command_runner: CommandRecorder,
    make_mcp: Callable[[Path, Config], FastMCP],
) -> None:
    config = Config(root_dir=tmp_path, tools=("ruff",))
    write_tool_settings(
        tmp_path / config.settings_file,
        RuffSettings(max_diagnostics=1, diagnostic_length=10),
        tool_name="ruff",
    )
    command_runner.add_result(
        ExecResult(
            exit_code=1,
            stdout=json.dumps(
                [
                    {
                        "code": "E501",
                        "message": "Line too long and it keeps going",
                        "filename": "a.py",
                        "location": {"row": 1, "column": 0},
                        "end_location": {"row": 1, "column": 10},
                        "fix": None,
                    }
                ]
            ),
        )
    )
    server = make_mcp(tmp_path, config)
    result = cast(
        RuffResult, await invoke_tool(server, "ruff_lint", {"paths": ["src"]})
    )
    assert command_runner.calls[-1].command == [
        "ruff",
        "check",
        "--output-format",
        "json",
        "src",
    ]
    assert result.exit_code == 1
    assert len(result.diagnostics) == 1
    assert result.diagnostics[0].message == "Line too l"


@pytest.mark.asyncio
async def test_pytest_invoke(
    tmp_path: Path,
    command_runner: CommandRecorder,
    make_mcp: Callable[[Path, Config], FastMCP],
) -> None:
    config = Config(root_dir=tmp_path, tools=("pytest",))
    write_tool_settings(
        tmp_path / config.settings_file,
        PytestSettings(test_args=("-x",)),
        tool_name="pytest",
    )
    command_runner.junit_report = (
        '<testsuite name="tests" tests="1" failures="0" errors="0" skipped="0" '
        'time="0.01"><testcase name="test_ok" classname="tests.test_ok" '
        'time="0.01" /></testsuite>'
    )
    command_runner.add_result(ExecResult(exit_code=0, stdout="pytest output"))

    server = make_mcp(tmp_path, config)
    result = cast(
        PytestResult, await invoke_tool(server, "pytest", {"paths": ["tests"]})
    )

    assert command_runner.calls[-1].command[0] == "pytest"
    assert command_runner.calls[-1].command[2:] == ["-x", "tests"]
    assert result.exit_code == 0
    assert result.suites[0].cases[0].outcome == "passed"


def test_pytest_junit_schema(tmp_path: Path) -> None:
    report = tmp_path / "pytest.xml"
    report.write_text(
        '<testsuite name="tests" tests="1" failures="1" errors="0" skipped="0" '
        + 'time="0.1"><testcase name="test_bad" classname="tests.test_bad" '
        + 'time="0.1"><failure message="boom">traceback</failure></testcase>'
        + "</testsuite>"
    )
    suites = parse_pytest_junit(report)
    assert suites[0].cases[0].outcome == "failed"
    assert suites[0].cases[0].message == "boom"


@pytest.mark.asyncio
async def test_basedpyright_invoke(
    tmp_path: Path,
    command_runner: CommandRecorder,
    make_mcp: Callable[[Path, Config], FastMCP],
) -> None:
    config = Config(root_dir=tmp_path, tools=("basedpyright",))
    write_tool_settings(
        tmp_path / config.settings_file,
        BasedpyrightSettings(max_diagnostics=1, diagnostic_length=10),
        tool_name="ruff",
    )

    command_runner.add_result(
        ExecResult(
            exit_code=1,
            stdout=json.dumps(
                {
                    "summary": {"errorCount": 1, "warningCount": 2},
                    "generalDiagnostics": [],
                }
            ),
        )
    )

    server = make_mcp(tmp_path, config)
    data = await invoke_tool(server, "basedpyright", {"paths": ["."]})
    result = cast(BPResult, data)

    assert command_runner.calls[-1].command == ["basedpyright", "--outputjson", "."]
    assert result.exit_code == 1
    assert result.errors == 1
    assert result.warnings == 2
