"""Regression tests for the canonical EquityCurve temporal contract."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from shared.contracts.equity_curve import EquityCurveData


def _curve(timestamps: tuple[datetime, ...]) -> EquityCurveData:
    return EquityCurveData(
        timestamps=timestamps,
        equity=tuple(Decimal(str(100 + index)) for index in range(len(timestamps))),
        drawdown=tuple(Decimal("0") for _ in timestamps),
    )


def test_rejects_duplicate_timestamps() -> None:
    first = datetime(2026, 1, 1, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="strictly ordered"):
        _curve((first, first))


def test_rejects_decreasing_timestamps() -> None:
    first = datetime(2026, 1, 1, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="strictly ordered"):
        _curve((first + timedelta(minutes=1), first))


def test_accepts_strictly_increasing_timestamps() -> None:
    first = datetime(2026, 1, 1, tzinfo=timezone.utc)
    curve = _curve((first, first + timedelta(minutes=1)))
    assert curve.timestamps[1] > curve.timestamps[0]
