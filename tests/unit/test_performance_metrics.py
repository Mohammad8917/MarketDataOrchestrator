"""Unit tests for deterministic performance metric calculation."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from shared.contracts.equity_curve import EquityCurveData
from strategy.evaluation.performance_metrics import calculate_performance_metrics


def curve(*values: str) -> EquityCurveData:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    equity = tuple(Decimal(value) for value in values)
    return EquityCurveData(
        timestamps=tuple(start + timedelta(hours=index) for index in range(len(equity))),
        equity=equity,
        drawdown=tuple(Decimal("0") for _ in equity),
    )


def test_calculates_total_return() -> None:
    metrics = calculate_performance_metrics(curve("100", "105", "110"))

    assert metrics.observations == 3
    assert metrics.initial_equity == Decimal("100")
    assert metrics.final_equity == Decimal("110")
    assert metrics.total_return == Decimal("0.1")
    assert metrics.max_drawdown == Decimal("0")


def test_calculates_max_drawdown_from_equity_peak() -> None:
    metrics = calculate_performance_metrics(curve("100", "120", "90", "110"))

    assert metrics.max_drawdown == Decimal("-0.25")


def test_rejects_empty_equity_curve() -> None:
    with pytest.raises(ValueError, match="at least one observation"):
        calculate_performance_metrics(curve())


def test_rejects_non_equity_curve_input() -> None:
    with pytest.raises(TypeError, match="EquityCurve"):
        calculate_performance_metrics(object())  # type: ignore[arg-type]
