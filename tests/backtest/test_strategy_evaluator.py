"""FILE: tests/backtest/test_strategy_evaluator.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-29
DATE_PERSIAN: 1405-07-07
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify deterministic strategy evaluation into canonical performance metrics.
LAYER: tests
OWNS: Strategy evaluator behavioral verification.
DOES_NOT_OWN: production strategy logic, execution simulation, persistence, release approval
DEPENDENCIES: pytest; backtest.strategy_evaluator; domain.common.timeframe; domain.market_data_event; shared.contracts.performance_metrics; strategy.trend.donchian
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from backtest.strategy_evaluator import StrategyEvaluator
from domain.common.timeframe import Timeframe
from domain.market_data_event import MarketDataEvent
from shared.contracts.performance_metrics import PerformanceMetrics
from strategy.trend.donchian import DonchianStrategy


def _event(index: int, close: str) -> MarketDataEvent:
    timestamp = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(hours=index)
    price = Decimal(close)
    return MarketDataEvent.create(
        provider="test",
        symbol="BTCUSDT",
        timeframe=Timeframe.parse("1h"),
        event_time=timestamp,
        received_at=timestamp,
        open=price,
        high=price,
        low=price,
        close=price,
        volume=Decimal("1"),
    )


def test_evaluate_returns_canonical_metrics() -> None:
    metrics = StrategyEvaluator(Decimal("100")).evaluate(
        (_event(0, "100"), _event(1, "100"), _event(2, "110")),
        DonchianStrategy(period=2),
    )

    assert isinstance(metrics, PerformanceMetrics)
    assert metrics.observations == 3
    assert metrics.initial_equity == Decimal("100")
    assert metrics.final_equity == Decimal("110")
    assert metrics.total_return == Decimal("0.1")
    assert metrics.max_drawdown == Decimal("0")


def test_evaluate_rejects_insufficient_history() -> None:
    with pytest.raises(ValueError, match="at least 2"):
        StrategyEvaluator().evaluate((_event(0, "100"),), DonchianStrategy(period=2))


def test_evaluate_preserves_next_bar_semantics() -> None:
    metrics = StrategyEvaluator(Decimal("100")).evaluate(
        (
            _event(0, "100"),
            _event(1, "110"),
            _event(2, "100"),
        ),
        DonchianStrategy(period=2),
    )

    assert metrics.final_equity == Decimal("100")
    assert metrics.max_drawdown == Decimal("0")
