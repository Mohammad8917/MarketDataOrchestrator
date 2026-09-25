from decimal import Decimal

import pytest

from shared.contracts.equity_curve import EquityCurveData
from strategy.evaluation.performance_metrics import PerformanceMetrics


def curve(*values: str) -> EquityCurveData:
    from datetime import datetime, timedelta, timezone

    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    equity = tuple(Decimal(value) for value in values)
    return EquityCurveData(
        timestamps=tuple(start + timedelta(hours=index) for index in range(len(equity))),
        equity=equity,
        drawdown=tuple(Decimal("0") for _ in equity),
    )


def test_metrics_compute_return_drawdown_and_positive_rate() -> None:
    metrics = PerformanceMetrics.from_equity(
        curve("100", "110", "99", "108"),
        periods_per_year=2190,
    )
    assert metrics.total_return == Decimal("0.08")
    assert metrics.max_drawdown == Decimal("-0.1")
    assert metrics.positive_return_rate == Decimal(2) / Decimal(3)
    assert metrics.sharpe_ratio is not None


def test_metrics_leave_sharpe_undefined_for_constant_returns() -> None:
    metrics = PerformanceMetrics.from_equity(
        curve("100", "100", "100"),
        periods_per_year=2190,
    )
    assert metrics.sharpe_ratio is None


def test_metrics_reject_invalid_inputs() -> None:
    with pytest.raises(ValueError, match="periods_per_year"):
        PerformanceMetrics.from_equity(curve("100"), periods_per_year=0)
    with pytest.raises(ValueError, match="must not be empty"):
        PerformanceMetrics.from_equity(curve(), periods_per_year=2190)
