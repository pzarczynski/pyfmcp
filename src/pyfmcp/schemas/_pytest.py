from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from xml.etree import ElementTree as ET

from pyfmcp.schemas._base import BaseResult

Outcome = Literal["passed", "failed", "error", "skipped", "xfailed", "xpassed"]


@dataclass(frozen=True, kw_only=True)
class Property:
    name: str
    value: str


@dataclass(frozen=True, kw_only=True)
class TestCase:
    name: str
    classname: str
    time: float
    outcome: Outcome
    message: str | None = None
    details: str | None = None
    properties: tuple[Property, ...] = ()
    stdout: str | None = None
    stderr: str | None = None


@dataclass(frozen=True, kw_only=True)
class TestSuite:
    name: str
    tests: int
    failures: int
    errors: int
    skipped: int
    time: float
    timestamp: str | None = None
    hostname: str | None = None
    properties: tuple[Property, ...] = ()
    cases: tuple[TestCase, ...] = ()


@dataclass(frozen=True, kw_only=True)
class PytestResult(BaseResult):
    suites: tuple[TestSuite, ...] = ()


def _text(element: ET.Element | None) -> str | None:
    if element is None:
        return None
    return element.text or ""


def _float_attribute(element: ET.Element, name: str) -> float:
    return float(element.get(name, "0"))


def _int_attribute(element: ET.Element, name: str) -> int:
    return int(element.get(name, "0"))


def _properties(parent: ET.Element) -> tuple[Property, ...]:
    properties = parent.find("properties")
    if properties is None:
        return ()
    return tuple(
        Property(name=prop.get("name", ""), value=prop.get("value", ""))
        for prop in properties.findall("property")
    )


def _parse_case(element: ET.Element) -> TestCase:
    failure = element.find("failure")
    error = element.find("error")
    skipped = element.find("skipped")
    detail = failure if failure is not None else error if error is not None else skipped
    if failure is not None:
        outcome: Outcome = "failed"
    elif error is not None:
        outcome = "error"
    elif skipped is not None and skipped.get("type") == "pytest.xfail":
        outcome = "xfailed"
    elif skipped is not None:
        outcome = "skipped"
    else:
        outcome = "passed"

    return TestCase(
        name=element.get("name", ""),
        classname=element.get("classname", ""),
        time=_float_attribute(element, "time"),
        outcome=outcome,
        message=detail.get("message") if detail is not None else None,
        details=_text(detail),
        properties=_properties(element),
        stdout=_text(element.find("system-out")),
        stderr=_text(element.find("system-err")),
    )


def _parse_suite(element: ET.Element) -> TestSuite:
    return TestSuite(
        name=element.get("name", ""),
        tests=_int_attribute(element, "tests"),
        failures=_int_attribute(element, "failures"),
        errors=_int_attribute(element, "errors"),
        skipped=_int_attribute(element, "skipped"),
        time=_float_attribute(element, "time"),
        timestamp=element.get("timestamp"),
        hostname=element.get("hostname"),
        properties=_properties(element),
        cases=tuple(_parse_case(case) for case in element.findall("testcase")),
    )


def parse_pytest_junit(path: str | Path) -> tuple[TestSuite, ...]:
    """Parse the suites emitted by pytest's ``--junitxml`` option."""
    root = ET.parse(path).getroot()
    elements = [root] if root.tag == "testsuite" else root.findall("testsuite")
    return tuple(_parse_suite(element) for element in elements)
