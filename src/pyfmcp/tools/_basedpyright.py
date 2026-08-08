from collections.abc import Callable

import msgspec
from fastmcp import FastMCP

from pyfmcp.schemas import ExecResult, SourcePosition
from pyfmcp.schemas._basedpyright import (
    BPDiagnostic,
    BPDiagnosticWire,
    BPOutput,
    BPResult,
)

from ._base import ToolContext, ToolSettings, ToolSpec, make_tool_handler


class BasedpyrightSettings(ToolSettings, frozen=True):
    """Arguments used to configure basedpyright checks."""

    max_diagnostics: int | None = None
    diagnostic_length: int | None = None


_DEFAULT_SETTINGS = BasedpyrightSettings()


def _convert_wire(wire: BPDiagnosticWire) -> BPDiagnostic:
    return BPDiagnostic(
        message=wire.message,
        filename=wire.file,
        severity=wire.severity,
        start=SourcePosition(
            line=wire.range.start.line + 1, column=wire.range.start.character + 1
        ),
        end=SourcePosition(
            line=wire.range.end.line + 1, column=wire.range.end.character + 1
        ),
        rule=wire.rule,
    )


def _parse_result(
    result: ExecResult, settings: BasedpyrightSettings = _DEFAULT_SETTINGS
) -> BPResult:
    output = msgspec.json.decode(result.stdout, type=BPOutput)
    diagnostics = tuple(_convert_wire(wire) for wire in output.generalDiagnostics)
    if settings.diagnostic_length is not None:
        diagnostics = tuple(
            BPDiagnostic(
                message=item.message[: settings.diagnostic_length],
                filename=item.filename,
                severity=item.severity,
                start=item.start,
                end=item.end,
                rule=item.rule,
            )
            for item in diagnostics
        )
    if settings.max_diagnostics is not None:
        diagnostics = diagnostics[: settings.max_diagnostics]
    return BPResult(
        diagnostics=diagnostics,
        errors=output.summary.errorCount,
        warnings=output.summary.warningCount,
        exit_code=result.exit_code,
    )


def _register(
    mcp: FastMCP,
    context: ToolContext,
    settings_loader: Callable[[], BasedpyrightSettings],
) -> None:
    handler = make_tool_handler(
        context,
        settings_loader,
        lambda _current, paths: ["basedpyright", "--outputjson", *paths],
        _parse_result,
    )

    @mcp.tool()
    def basedpyright(  # pyright: ignore[reportUnusedFunction]
        paths: tuple[str, ...] = (".",),
    ) -> BPResult:
        """Run basedpyright diagnostics"""
        return handler(paths)


BASEDPYRIGHT_SPEC = ToolSpec[BasedpyrightSettings, BPResult](
    name="basedpyright",
    settings_type=BasedpyrightSettings,
    register_tool=_register,
)
