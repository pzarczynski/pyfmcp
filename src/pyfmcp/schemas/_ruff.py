from dataclasses import dataclass

import msgspec

from ._base import BaseResult, SourcePosition


class _Location(msgspec.Struct, kw_only=True):
    row: int
    column: int


class RuffDiagnosticWire(msgspec.Struct, kw_only=True):
    code: str | None = None
    message: str
    filename: str
    location: _Location
    end_location: _Location | None = None
    fix: object | None = None


@dataclass(frozen=True, kw_only=True)
class RuffDiagnostic:
    code: str | None = None
    message: str
    filename: str
    start: SourcePosition
    end: SourcePosition | None = None
    fixable: bool = False


@dataclass(frozen=True, kw_only=True)
class RuffResult(BaseResult):
    diagnostics: tuple[RuffDiagnostic, ...]
