"""Adversarial tests for the strategy-comparison runtime boundary."""

from decimal import Decimal

import pytest

from shared.contracts.performance_metrics import PerformanceMetricsData
from shared.contracts.strategy_comparison import StrategyComparisonData


def _metrics() -> PerformanceMetricsData:
    initial = Decimal("100")
    final = Decimal("110")
    return PerformanceMetricsData(
        observations=2,
        initial_equity=initial,
        final_equity=final,
        total_return=(final - initial) / initial,
        max_drawdown=Decimal("0"),
    )


@pytest.mark.parametrize("entries", [[], [("alpha", _metrics())], (("alpha", _metrics()), ["beta", _metrics()]), (("alpha", _metrics(), "extra"),), (("alpha",),), (("alpha",),)], ids=["list", "single-list", "nested-list", "wrong-arity-3", "wrong-arity-1", "wrong-arity-1-again"])
def test_strategy_comparison_rejects_non_tuple_or_malformed_entries(entries: object) -> None:
    with pytest.raises((ValueError, TypeError)):
        StrategyComparisonData(entries=entries)  # type: ignore[arg-type]


def test_strategy_comparison_rejects_whitespace_strategy_name() -> None:
    with pytest.raises(ValueError, match="strategy name must be a non-empty string"):
        StrategyComparisonData(entries=(("   ", _metrics()),))


def test_strategy_comparison_accepts_immutable_ordered_entries() -> None:
    result = StrategyComparisonData(entries=(("alpha", _metrics()), ("beta", _metrics())))
    assert result.entries[0][0] == "alpha"
    assert result.entries[1][0] == "beta"
