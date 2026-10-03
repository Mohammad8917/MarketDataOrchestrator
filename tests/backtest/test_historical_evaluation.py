"""Verify fail-closed runtime and temporal validation for historical evaluation."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import cast

import pytest

from backtest.historical_evaluation import MultiMarketHistoricalEvaluationHarness
from domain.common.timeframe import Timeframe
from domain.market_data_event import MarketDataEvent
from shared.contracts.performance_metrics import PerformanceMetricsData


def _event(index: int, symbol: str = "BTCUSDT") -> MarketDataEvent:
    timestamp = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(hours=index)
    price = Decimal("100") + Decimal(index)
    return MarketDataEvent.create(
        provider="test",
        symbol=symbol,
        timeframe=Timeframe.parse("1h"),
        event_time=timestamp,
        received_at=timestamp,
        open=price,
        high=price,
        low=price,
        close=price,
        volume=Decimal("1"),
    )


class ValidEvaluator:
    def evaluate(self, events: tuple[MarketDataEvent, ...]) -> PerformanceMetricsData:
        return PerformanceMetricsData(
            observations=len(events),
            initial_equity=Decimal("100"),
            final_equity=Decimal("101"),
            total_return=Decimal("0.01"),
            max_drawdown=Decimal("0"),
        )


@pytest.mark.parametrize("events", [None, [], [_event(0)], "events"])
def test_rejects_invalid_event_containers(events: object) -> None:
    with pytest.raises(ValueError, match="events must be a tuple"):
        MultiMarketHistoricalEvaluationHarness().evaluate(events, ValidEvaluator())  # type: ignore[arg-type]


def test_rejects_invalid_event_element() -> None:
    with pytest.raises(ValueError, match="events must contain only MarketDataEvent"):
        MultiMarketHistoricalEvaluationHarness().evaluate((_event(0), object()), ValidEvaluator())  # type: ignore[arg-type]


def test_rejects_empty_stream() -> None:
    with pytest.raises(ValueError, match="events must not be empty"):
        MultiMarketHistoricalEvaluationHarness().evaluate((), ValidEvaluator())


def test_rejects_non_strict_temporal_order() -> None:
    with pytest.raises(ValueError, match="strictly ordered"):
        MultiMarketHistoricalEvaluationHarness().evaluate((_event(1), _event(0)), ValidEvaluator())


def test_rejects_mixed_stream_identity() -> None:
    with pytest.raises(ValueError, match="one provider, symbol, and timeframe"):
        MultiMarketHistoricalEvaluationHarness().evaluate(
            (_event(0), _event(1, "XAUUSD")), ValidEvaluator()
        )


def test_rejects_invalid_evaluator() -> None:
    with pytest.raises(TypeError, match="evaluator must implement HistoricalEvaluator"):
        MultiMarketHistoricalEvaluationHarness().evaluate(  # type: ignore[arg-type]
            (_event(0),), object()
        )


def test_rejects_invalid_evaluator_output() -> None:
    class InvalidEvaluator:
        def evaluate(
            self, events: tuple[MarketDataEvent, ...]
        ) -> PerformanceMetricsData:
            return cast(PerformanceMetricsData, object())

    with pytest.raises(TypeError, match="evaluator must return PerformanceMetricsData"):
        MultiMarketHistoricalEvaluationHarness().evaluate((_event(0),), InvalidEvaluator())


def test_returns_validated_stream_output() -> None:
    result = MultiMarketHistoricalEvaluationHarness().evaluate(
        (_event(0), _event(1)), ValidEvaluator()
    )

    assert isinstance(result, PerformanceMetricsData)
    assert result.observations == 2
