"""FILE: tests/unit/test_historical_evaluation.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify market-agnostic historical stream validation and delegation.
LAYER: tests
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from backtest.historical_evaluation import MultiMarketHistoricalEvaluationHarness
from domain.common.timeframe import Timeframe
from domain.market_data_event import MarketDataEvent
from shared.contracts.performance_metrics import PerformanceMetricsData


class StubEvaluator:
    def __init__(self) -> None:
        self.calls: list[tuple[MarketDataEvent, ...]] = []

    def evaluate(self, events: tuple[MarketDataEvent, ...]) -> PerformanceMetricsData:
        self.calls.append(events)
        return PerformanceMetricsData(
            observations=len(events),
            initial_equity=Decimal("1"),
            final_equity=Decimal("1"),
            total_return=Decimal("0"),
            max_drawdown=Decimal("0"),
        )


def event(
    index: int,
    *,
    provider: str,
    symbol: str,
    timeframe: str = "4h",
) -> MarketDataEvent:
    moment = datetime(2026, 1, 1, tzinfo=UTC) + timedelta(hours=4 * index)
    return MarketDataEvent.create(
        provider=provider,
        symbol=symbol,
        timeframe=Timeframe.parse(timeframe),
        event_time=moment,
        received_at=moment,
        open=Decimal("100"),
        high=Decimal("101"),
        low=Decimal("99"),
        close=Decimal("100"),
        volume=Decimal("1"),
    )


@pytest.mark.parametrize(
    ("provider", "symbol"),
    (("binance", "BTCUSDT"), ("oanda", "EURUSD"), ("test", "XAUUSD")),
)
def test_harness_is_market_agnostic(provider: str, symbol: str) -> None:
    evaluator = StubEvaluator()
    events = (event(0, provider=provider, symbol=symbol), event(1, provider=provider, symbol=symbol))

    result = MultiMarketHistoricalEvaluationHarness().evaluate(events, evaluator)

    assert result.observations == 2
    assert evaluator.calls == [events]


def test_harness_rejects_mixed_market_stream() -> None:
    evaluator = StubEvaluator()
    events = (
        event(0, provider="binance", symbol="BTCUSDT"),
        event(1, provider="oanda", symbol="EURUSD"),
    )

    with pytest.raises(ValueError, match="one provider, symbol, and timeframe"):
        MultiMarketHistoricalEvaluationHarness().evaluate(events, evaluator)


def test_harness_rejects_unsorted_stream() -> None:
    evaluator = StubEvaluator()
    events = (
        event(1, provider="binance", symbol="BTCUSDT"),
        event(0, provider="binance", symbol="BTCUSDT"),
    )

    with pytest.raises(ValueError, match="strictly ordered"):
        MultiMarketHistoricalEvaluationHarness().evaluate(events, evaluator)


def test_harness_rejects_empty_or_invalid_evaluator() -> None:
    harness = MultiMarketHistoricalEvaluationHarness()

    with pytest.raises(ValueError, match="must not be empty"):
        harness.evaluate((), StubEvaluator())

    with pytest.raises(TypeError, match="HistoricalEvaluator"):
        harness.evaluate((event(0, provider="binance", symbol="BTCUSDT"),), object())  # type: ignore[arg-type]
