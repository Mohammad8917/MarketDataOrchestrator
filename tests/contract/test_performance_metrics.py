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



@pytest.mark.parametrize(
    "value",
    [True, 0, -1],
)
def test_performance_metrics_rejects_non_positive_observations(value: object) -> None:
    with pytest.raises(ValueError, match="observations must be a positive integer"):
        PerformanceMetricsData(
            observations=value,  # type: ignore[arg-type]
            initial_equity=Decimal("100"),
            final_equity=Decimal("110"),
            total_return=Decimal("0.1"),
            max_drawdown=Decimal("0"),
        )


@pytest.mark.parametrize(
    "field", ["initial_equity", "final_equity", "total_return", "max_drawdown"]
)
def test_performance_metrics_rejects_non_finite_decimal_values(field: str) -> None:
    values: dict[str, object] = {
        "observations": 2,
        "initial_equity": Decimal("100"),
        "final_equity": Decimal("110"),
        "total_return": Decimal("0.1"),
        "max_drawdown": Decimal("0"),
    }
    values[field] = Decimal("NaN")
    with pytest.raises(ValueError, match=f"{field} must be a finite Decimal value"):
        PerformanceMetricsData(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize("field", ["initial_equity", "final_equity"])
def test_performance_metrics_rejects_non_positive_equity(field: str) -> None:
    values: dict[str, object] = {
        "observations": 2,
        "initial_equity": Decimal("100"),
        "final_equity": Decimal("110"),
        "total_return": Decimal("0.1"),
        "max_drawdown": Decimal("0"),
    }
    values[field] = Decimal("0")
    with pytest.raises(ValueError, match="equity values must be positive"):
        PerformanceMetricsData(**values)  # type: ignore[arg-type]


def test_performance_metrics_rejects_positive_max_drawdown() -> None:
    with pytest.raises(ValueError, match="max_drawdown cannot be positive"):
        PerformanceMetricsData(
            observations=2,
            initial_equity=Decimal("100"),
            final_equity=Decimal("110"),
            total_return=Decimal("0.1"),
            max_drawdown=Decimal("0.01"),
        )


def test_performance_metrics_rejects_inconsistent_total_return() -> None:
    with pytest.raises(ValueError, match="total_return does not match equity values"):
        PerformanceMetricsData(
            observations=2,
            initial_equity=Decimal("100"),
            final_equity=Decimal("110"),
            total_return=Decimal("0.2"),
            max_drawdown=Decimal("0"),
        )
