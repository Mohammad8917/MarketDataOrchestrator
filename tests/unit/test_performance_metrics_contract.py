"""Contract tests for the immutable performance metrics boundary."""

from decimal import Decimal

import pytest

from shared.contracts.performance_metrics import (
    PerformanceMetrics,
    PerformanceMetricsData,
)


def test_performance_metrics_data_conforms_to_protocol() -> None:
    metrics = PerformanceMetricsData(
        observations=3,
        initial_equity=Decimal("100"),
        final_equity=Decimal("110"),
        total_return=Decimal("0.1"),
        max_drawdown=Decimal("-0.05"),
    )

    assert isinstance(metrics, PerformanceMetrics)


def test_rejects_non_positive_observations() -> None:
    with pytest.raises(ValueError, match="positive integer"):
        PerformanceMetricsData(
            observations=0,
            initial_equity=Decimal("100"),
            final_equity=Decimal("100"),
            total_return=Decimal("0"),
            max_drawdown=Decimal("0"),
        )


def test_rejects_non_decimal_values() -> None:
    with pytest.raises(ValueError, match="finite Decimal"):
        PerformanceMetricsData(
            observations=2,
            initial_equity=100,  # type: ignore[arg-type]
            final_equity=Decimal("100"),
            total_return=Decimal("0"),
            max_drawdown=Decimal("0"),
        )


def test_rejects_positive_max_drawdown() -> None:
    with pytest.raises(ValueError, match="cannot be positive"):
        PerformanceMetricsData(
            observations=2,
            initial_equity=Decimal("100"),
            final_equity=Decimal("110"),
            total_return=Decimal("0.1"),
            max_drawdown=Decimal("0.01"),
        )


def test_rejects_inconsistent_total_return() -> None:
    with pytest.raises(ValueError, match="does not match"):
        PerformanceMetricsData(
            observations=2,
            initial_equity=Decimal("100"),
            final_equity=Decimal("110"),
            total_return=Decimal("0.2"),
            max_drawdown=Decimal("0"),
        )
