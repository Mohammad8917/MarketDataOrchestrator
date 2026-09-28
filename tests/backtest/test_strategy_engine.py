"""Tests for strategy-aware backtest execution."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from backtest.strategy_engine import StrategyBacktestEngine
from domain.common.timeframe import Timeframe
from domain.market_data_event import MarketDataEvent
from shared.contracts.market_bar import MarketBar
from strategy.trend.donchian import DonchianPosition, DonchianStrategy


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


class FakeStrategy:
    def __init__(self, signals: tuple[DonchianPosition, ...]) -> None:
        self._signals = signals

    def signals(self, events: tuple[MarketBar, ...]) -> tuple[DonchianPosition, ...]:
        return self._signals


def test_next_bar_execution() -> None:
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


def test_flat_position_preserves_equity() -> None:
    curve = StrategyBacktestEngine().run(
        (event(0, "10"), event(1, "12")),
        FakeStrategy((DonchianPosition.FLAT, DonchianPosition.FLAT)),
    )
    assert curve.equity == (Decimal("1"), Decimal("1"))


def test_drawdown_is_calculated() -> None:
    curve = StrategyBacktestEngine().run(
        (event(0, "10"), event(1, "20"), event(2, "10")),
        FakeStrategy((DonchianPosition.LONG, DonchianPosition.LONG)),
    )
    assert curve.drawdown[-1] == Decimal("-0.5")


def test_short_history_is_allowed() -> None:
    curve = StrategyBacktestEngine().run(
        (event(0, "10"), event(1, "10")),
        DonchianStrategy(period=3),
    )
    assert curve.equity == (Decimal("1"), Decimal("1"))


def test_rejects_invalid_engine_input() -> None:
    with pytest.raises(ValueError, match="initial_capital"):
        StrategyBacktestEngine(Decimal("0"))
    with pytest.raises(ValueError, match="at least two"):
        StrategyBacktestEngine().run((event(0, "10"),), DonchianStrategy())


def test_rejects_non_strategy() -> None:
    with pytest.raises(TypeError, match="implement PositionStrategy"):
        StrategyBacktestEngine().run((event(0, "10"), event(1, "11")), object())


def test_rejects_wrong_signal_count() -> None:
    class WrongCount:
        def signals(self, events: tuple[MarketBar, ...]) -> tuple[DonchianPosition, ...]:
            return ()

    with pytest.raises(ValueError, match="one signal"):
        StrategyBacktestEngine().run((event(0, "10"), event(1, "11")), WrongCount())


def test_rejects_unsupported_position() -> None:
    class BadStrategy:
        def signals(self, events: tuple[MarketBar, ...]) -> tuple[DonchianPosition, ...]:
            return (object(), object())  # type: ignore[return-value]

    with pytest.raises(ValueError, match="unsupported position"):
        StrategyBacktestEngine().run((event(0, "10"), event(1, "11")), BadStrategy())
