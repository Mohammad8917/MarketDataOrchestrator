"""FILE: tests/unit/test_donchian_evaluation.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify deterministic Donchian-to-performance composition.
LAYER: tests
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from backtest.donchian_evaluation import DonchianPerformanceEvaluator
from domain.common.timeframe import Timeframe
from domain.market_data_event import MarketDataEvent


def event(index: int, *, high: int, low: int, close: int) -> MarketDataEvent:
    moment = datetime(2026, 1, 1, tzinfo=UTC) + timedelta(minutes=index)
    return MarketDataEvent.create(
        provider="test",
        symbol="BTCUSDT",
        timeframe=Timeframe.parse("1m"),
        event_time=moment,
        received_at=moment,
        open=Decimal(str(close)),
        high=Decimal(str(high)),
        low=Decimal(str(low)),
        close=Decimal(str(close)),
        volume=Decimal("1"),
    )


def test_evaluator_composes_donchian_equity_with_performance_metrics() -> None:
    events = (
        event(0, high=10, low=8, close=9),
        event(1, high=11, low=8, close=10),
        event(2, high=13, low=9, close=13),
        event(3, high=14, low=10, close=14),
        event(4, high=11, low=6, close=7),
    )

    metrics = DonchianPerformanceEvaluator(period=2).evaluate(events)

    assert metrics.observations == 5
    assert metrics.initial_equity == Decimal("1")
    assert metrics.final_equity == Decimal("7") / Decimal("13")
    assert metrics.total_return == Decimal("7") / Decimal("13") - Decimal("1")
    assert metrics.max_drawdown == Decimal("-0.5")
