from datetime import datetime, timedelta, timezone
from decimal import Decimal

from backtest.strategy_engine import StrategyBacktestEngine
from domain.common.timeframe import Timeframe
from domain.market_data_event import MarketDataEvent
from strategy.trend.donchian import DonchianStrategy


def event(
    index: int, close: str, high: str | None = None, low: str | None = None
) -> MarketDataEvent:
    value = Decimal(close)
    timestamp = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(hours=4 * index)
    return MarketDataEvent.create(
        provider="fixture",
        symbol="BTCUSDT",
        timeframe=Timeframe.parse("4h"),
        event_time=timestamp,
        received_at=timestamp,
        open=value,
        high=Decimal(high) if high is not None else value,
        low=Decimal(low) if low is not None else value,
        close=value,
        volume=Decimal("1"),
    )


def test_strategy_engine_applies_signal_on_next_bar() -> None:
    events = (
        event(0, "10", "11", "9"),
        event(1, "11", "12", "10"),
        event(2, "12", "13", "11"),
        event(3, "14", "15", "13"),
        event(4, "21", "22", "20"),
    )
    curve = StrategyBacktestEngine().run(events, DonchianStrategy(period=3))
    assert curve.equity == (
        Decimal("1"),
        Decimal("1"),
        Decimal("1"),
        Decimal("1"),
        Decimal("1.5"),
    )


def test_strategy_engine_accepts_short_history_without_lookahead() -> None:
    events = (
        event(0, "10"),
        event(1, "10"),
    )
    curve = StrategyBacktestEngine().run(events, DonchianStrategy(period=3))
    assert curve.equity == (Decimal("1"), Decimal("1"))
