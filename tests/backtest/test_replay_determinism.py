"""FILE: tests/backtest/test_replay_determinism.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-29
DATE_PERSIAN: 1405-07-07
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify deterministic repeated historical replay.
LAYER: tests
OWNS: Replay determinism assertions.
DOES_NOT_OWN: Persistence implementation or release evidence.
DEPENDENCIES: datetime, decimal, backtest.strategy_engine, domain.common.timeframe, domain.market_data_event, strategy.trend.donchian
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from backtest.strategy_engine import StrategyBacktestEngine
from domain.common.timeframe import Timeframe
from domain.market_data_event import MarketDataEvent
from strategy.trend.donchian import DonchianStrategy


def event(index: int, close: int) -> MarketDataEvent:
    t = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=index)
    return MarketDataEvent.create(
        provider="test",
        symbol="BTCUSDT",
        timeframe=Timeframe.parse("1m"),
        event_time=t,
        received_at=t,
        open=Decimal(str(close)),
        high=Decimal(str(close + 1)),
        low=Decimal(str(close - 1)),
        close=Decimal(str(close)),
        volume=Decimal("1"),
    )


def test_same_replay_produces_identical_equity_curve() -> None:
    events = tuple(event(i, c) for i, c in enumerate((9, 10, 13, 14, 12)))
    engine = StrategyBacktestEngine(Decimal("1000"))
    first = engine.run(events, DonchianStrategy(period=2))
    second = engine.run(events, DonchianStrategy(period=2))
    assert first.timestamps == second.timestamps
    assert first.equity == second.equity
    assert first.drawdown == second.drawdown
