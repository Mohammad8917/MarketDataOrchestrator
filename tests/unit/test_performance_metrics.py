"""Tests for deterministic performance metrics."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from types import SimpleNamespace
from typing import cast

import pytest

from shared.contracts.equity_curve import EquityCurve, EquityCurveData
from strategy.evaluation.performance_metrics import PerformanceMetrics


def curve(*values: str) -> EquityCurveData:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    equity = tuple(Decimal(value) for value in values)
    return EquityCurveData(
        timestamps=tuple(start + timedelta(hours=i) for i in range(len(equity))),
        equity=equity,
        drawdown=tuple(Decimal("0") for _ in equity),
    )


def invalid_curve(*values: str) -> EquityCurve:
    """Build an intentionally invalid curve to exercise metric validation."""
    return cast(
        EquityCurve,
        SimpleNamespace(equity=tuple(Decimal(value) for value in values)),
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


def test_rejects_non_positive_equity() -> None:
    for values in (("100", "0"), ("100", "-1"), ("100", "100", "-1")):
        with pytest.raises(
            ValueError,
            match=r"\Aequity values must be finite and positive\Z",
        ):
            PerformanceMetrics.from_equity(
                invalid_curve(*values),
                periods_per_year=2190,
            )


@pytest.mark.parametrize("value", ("NaN", "Infinity", "-Infinity"))
def test_rejects_non_finite_equity(value: str) -> None:
    with pytest.raises(
        ValueError,
        match=r"\Aequity values must be finite and positive\Z",
    ):
        PerformanceMetrics.from_equity(
            invalid_curve("100", value),
            periods_per_year=2190,
        )


def test_rejects_non_positive_periods_per_year() -> None:
    with pytest.raises(
        ValueError,
        match=r"\Aperiods_per_year must be positive\Z",
    ):
        PerformanceMetrics.from_equity(
            invalid_curve("100"),
            periods_per_year=0,
        )


def test_rejects_empty_equity() -> None:
    with pytest.raises(
        ValueError,
        match=r"\Aequity must not be empty\Z",
    ):
        PerformanceMetrics.from_equity(
            invalid_curve(),
            periods_per_year=2190,
        )
