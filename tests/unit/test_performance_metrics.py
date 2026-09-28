"""Tests for deterministic performance metrics."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from shared.contracts.equity_curve import EquityCurveData
from strategy.evaluation.performance_metrics import PerformanceMetrics


def curve(*values: str) -> EquityCurveData:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    equity = tuple(Decimal(value) for value in values)
    return EquityCurveData(
        timestamps=tuple(start + timedelta(hours=i) for i in range(len(equity))),
        equity=equity,
        drawdown=tuple(Decimal("0") for _ in equity),
    )


def test_metrics_compute_all_values() -> None:
    metrics = PerformanceMetrics.from_equity(
        curve("100", "110", "99", "108"),
        periods_per_year=2190,
    )
    assert metrics.total_return == Decimal("0.08")
    assert metrics.max_drawdown == Decimal("-0.1")
    assert metrics.positive_return_rate == Decimal(2) / Decimal(3)
    assert metrics.sharpe_ratio is not None


def test_constant_returns_have_no_sharpe() -> None:
    assert (
        PerformanceMetrics.from_equity(
            curve("100", "100", "100"),
            periods_per_year=2190,
        ).sharpe_ratio
        is None
    )


def test_single_equity_value_has_no_return_series() -> None:
    metrics = PerformanceMetrics.from_equity(curve("100"), periods_per_year=2190)
    assert metrics.sharpe_ratio is None
    assert metrics.positive_return_rate == Decimal("0")


@pytest.mark.parametrize(
    "values,periods,message",
    [
        (("100",), 0, "periods_per_year"),
        ((), 2190, "must not be empty"),
        (("100", "0"), 2190, "must be positive"),
    ],
)
def test_rejects_invalid_inputs(
    values: tuple[str, ...],
    periods: int,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        PerformanceMetrics.from_equity(curve(*values), periods_per_year=periods)
