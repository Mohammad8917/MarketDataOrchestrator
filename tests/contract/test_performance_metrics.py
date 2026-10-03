"""Contract tests for the performance metrics boundary."""

from decimal import Decimal

import pytest

from shared.contracts.performance_metrics import PerformanceMetricsData


def _valid() -> PerformanceMetricsData:
    return PerformanceMetricsData(
        observations=2,
        initial_equity=Decimal("100"),
        final_equity=Decimal("110"),
        total_return=Decimal("0.1"),
        max_drawdown=Decimal("0"),
    )


def test_performance_metrics_accepts_valid_data() -> None:
    assert _valid().total_return == Decimal("0.1")


@pytest.mark.parametrize("value", ["2", 2.0, None, object()])
def test_performance_metrics_rejects_invalid_observations_runtime_types(value: object) -> None:
    with pytest.raises(ValueError, match="observations must be a positive integer"):
        PerformanceMetricsData(
            observations=value,  # type: ignore[arg-type]
            initial_equity=Decimal("100"),
            final_equity=Decimal("110"),
            total_return=Decimal("0.1"),
            max_drawdown=Decimal("0"),
        )
