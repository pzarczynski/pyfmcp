from __future__ import annotations

from dataclasses import dataclass

import msgspec

from ._base import BaseResult, SourcePosition


class _Point(msgspec.Struct, kw_only=True):
    line: int
    character: int


class _Range(msgspec.Struct, kw_only=True):
    start: _Point
    end: _Point


class _Summary(msgspec.Struct, kw_only=True):
    errorCount: int
    warningCount: int
    informationCount: int = 0


class BPDiagnosticWire(msgspec.Struct, kw_only=True):
    range: _Range
    severity: str
    message: str
    file: str
    rule: str | None = None


class BPOutput(msgspec.Struct, kw_only=True):
    summary: _Summary
    generalDiagnostics: tuple[BPDiagnosticWire, ...] = ()


@dataclass(frozen=True, kw_only=True)
class BPDiagnostic:
    message: str
    filename: str
    severity: str
    start: SourcePosition
    end: SourcePosition | None = None
    rule: str | None = None


@dataclass(frozen=True, kw_only=True)
class BPResult(BaseResult):
    diagnostics: tuple[BPDiagnostic, ...]
    errors: int
    warnings: int
