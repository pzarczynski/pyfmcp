from collections.abc import Callable

from fastmcp import FastMCP

from pyfmcp.schemas import ExecResult, SourcePosition
from pyfmcp.schemas._ruff import RuffDiagnostic, RuffDiagnosticWire, RuffResult

from ._base import ToolContext, ToolSettings, ToolSpec, decode_json, make_tool_handler


class RuffSettings(ToolSettings, frozen=True):
    """Arguments used to configure Ruff checks."""

    max_diagnostics: int | None = None
    diagnostic_length: int | None = None


_DEFAULT_SETTINGS = RuffSettings()


def _parse_wire(wire: RuffDiagnosticWire) -> RuffDiagnostic:
    return RuffDiagnostic(
        code=wire.code,
        message=wire.message,
        filename=wire.filename,
        start=SourcePosition(line=wire.location.row, column=wire.location.column + 1),
        end=(
            SourcePosition(
                line=wire.end_location.row, column=wire.end_location.column + 1
            )
            if wire.end_location
            else None
        ),
        fixable=wire.fix is not None,
    )


def _parse_result(
    result: ExecResult, settings: RuffSettings = _DEFAULT_SETTINGS
) -> RuffResult:
    wire = decode_json(result.stdout, type_=list[RuffDiagnosticWire])
    diagnostics = tuple(_parse_wire(item) for item in wire)
    if settings.diagnostic_length is not None:
        diagnostics = tuple(
            RuffDiagnostic(
                code=item.code,
                message=item.message[: settings.diagnostic_length],
                filename=item.filename,
                start=item.start,
                end=item.end,
                fixable=item.fixable,
            )
            for item in diagnostics
        )
    if settings.max_diagnostics is not None:
        diagnostics = diagnostics[: settings.max_diagnostics]
    return RuffResult(diagnostics=diagnostics, exit_code=result.exit_code)


def _register(
    mcp: FastMCP, context: ToolContext, settings_loader: Callable[[], RuffSettings]
) -> None:
    handler = make_tool_handler(
        context,
        settings_loader,
        lambda _current, paths: ["ruff", "check", "--output-format", "json", *paths],
        _parse_result,
    )

    @mcp.tool()
    def ruff_lint(  # pyright: ignore[reportUnusedFunction]
        paths: tuple[str, ...] = (".",),
    ) -> RuffResult:
        """Run Ruff diagnostics"""
        return handler(paths)


RUFF_SPEC = ToolSpec[RuffSettings, RuffResult](
    name="ruff_lint",
    settings_type=RuffSettings,
    register_tool=_register,
)
