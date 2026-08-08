from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class BaseResult:
    """Common result metadata returned by a tool."""

    exit_code: int


@dataclass(frozen=True, kw_only=True)
class ExecResult(BaseResult):
    """Captured subprocess output and its exit status."""

    stdout: str = ""
    stderr: str = ""


@dataclass(frozen=True, kw_only=True)
class SourcePosition:
    """One-based diagnostic location in a source file."""

    line: int
    column: int
