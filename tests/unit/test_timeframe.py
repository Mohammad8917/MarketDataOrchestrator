"""FILE: tests/unit/test_timeframe.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify Timeframe parsing, invariants, serialization, and duration behavior.
LAYER: tests
OWNS: Unit-level acceptance tests for the domain Timeframe value object.
DOES_NOT_OWN: production timeframe behavior, provider aliases, scheduling, or higher-level market logic.
DEPENDENCIES: domain.common.timeframe, pytest
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import timedelta

import pytest

from domain.common.timeframe import Timeframe


@pytest.mark.parametrize("value, expected", [
    ("1m", timedelta(minutes=1)),
    ("5m", timedelta(minutes=5)),
    ("1h", timedelta(hours=1)),
    ("4h", timedelta(hours=4)),
    ("1d", timedelta(days=1)),
    ("1w", timedelta(weeks=1)),
])
def test_parse_and_duration(value: str, expected: timedelta) -> None:
    timeframe = Timeframe.parse(value)
    assert timeframe.code == value
    assert timeframe.duration == expected
    assert str(timeframe) == value


@pytest.mark.parametrize("value", ["0m", "-1m", "1x", "m", "1", "1.5h", "01h", ""])
def test_parse_rejects_non_canonical_values(value: str) -> None:
    with pytest.raises(ValueError):
        Timeframe.parse(value)


def test_parse_rejects_non_string() -> None:
    with pytest.raises(TypeError):
        Timeframe.parse(5)  # type: ignore[arg-type]


def test_constructor_rejects_invalid_unit_and_value() -> None:
    with pytest.raises(ValueError):
        Timeframe(0, "m")
    with pytest.raises(ValueError):
        Timeframe(1, "x")


def test_timeframe_is_immutable() -> None:
    timeframe = Timeframe.parse("15m")
    with pytest.raises((AttributeError, TypeError)):
        timeframe.value = 30  # type: ignore[misc]
