from collections.abc import Callable
from pathlib import Path
from tempfile import TemporaryDirectory

from fastmcp import FastMCP

from pyfmcp.schemas import ExecResult
from pyfmcp.schemas._pytest import PytestResult, parse_pytest_junit

from ._base import ToolContext, ToolSettings, ToolSpec


class PytestSettings(ToolSettings, frozen=True):
    """Arguments appended to pytest invocations."""

    test_args: tuple[str, ...] = ()


def _run_pytest(
    context: ToolContext,
    settings: PytestSettings,
    paths: tuple[str, ...],
) -> PytestResult:
    with TemporaryDirectory() as temporary_directory:
        report = Path(temporary_directory) / "pytest.xml"
        command = [
            "pytest",
            f"--junitxml={report}",
            *settings.test_args,
            *paths,
        ]
        result: ExecResult = context.runner(command, settings.timeout, context.root)
        suites = parse_pytest_junit(report)
    return PytestResult(exit_code=result.exit_code, suites=suites)


def _register(
    mcp: FastMCP, context: ToolContext, settings_loader: Callable[[], PytestSettings]
) -> None:
    @mcp.tool()
    def pytest(  # pyright: ignore[reportUnusedFunction]
        paths: tuple[str, ...] = ("tests",),
    ) -> PytestResult:
        """Run pytest and return its JUnit XML report."""
        return _run_pytest(context, settings_loader(), paths)


PYTEST_SPEC = ToolSpec[PytestSettings, PytestResult](
    name="pytest",
    settings_type=PytestSettings,
    register_tool=_register,
)
