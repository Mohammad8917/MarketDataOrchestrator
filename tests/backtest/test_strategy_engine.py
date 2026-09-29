"""Tests for strategy backtest execution."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from backtest.strategy_engine import StrategyBacktestEngine
from domain.common.timeframe import Timeframe
from domain.market_data_event import MarketDataEvent
from strategy.trend.donchian import DonchianStrategy


def event(
    index: int,
    *,
    high: int = 12,
    low: int = 8,
    close: int = 10,
) -> MarketDataEvent:
    timestamp = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=index)
    return MarketDataEvent.create(
        provider="test",
        symbol="BTCUSDT",
        timeframe=Timeframe.parse("1m"),
        event_time=timestamp,
        received_at=timestamp,
        open=Decimal("10"),
        high=Decimal(str(high)),
        low=Decimal(str(low)),
        close=Decimal(str(close)),
        volume=Decimal("1"),
    )


def test_initial_capital_must_be_decimal() -> None:
    with pytest.raises(TypeError, match="must be Decimal"):
        StrategyBacktestEngine(10000)  # type: ignore[arg-type]


def test_initial_capital_must_be_positive_and_finite() -> None:
    with pytest.raises(ValueError, match="positive finite"):
        StrategyBacktestEngine(Decimal("0"))
    with pytest.raises(ValueError, match="positive finite"):
        StrategyBacktestEngine(Decimal("NaN"))


def test_requires_two_events() -> None:
    with pytest.raises(ValueError, match="at least 2"):
        StrategyBacktestEngine().run((event(0),), DonchianStrategy(period=2))


def test_requires_historical_strategy() -> None:
    with pytest.raises(TypeError, match="HistoricalStrategy"):
        StrategyBacktestEngine().run((event(0), event(1)), object())  # type: ignore[arg-type]


def test_requires_strict_event_order() -> None:
    first = event(0)
    with pytest.raises(ValueError, match="strictly ordered"):
        StrategyBacktestEngine().run((first, first), DonchianStrategy(period=2))


def test_uses_next_bar_execution_semantics() -> None:
    events = (
        event(0, high=10, low=8, close=9),
        event(1, high=11, low=8, close=10),
        event(2, high=12, low=9, close=13),
        event(3, high=14, low=10, close=14),
    )

    curve = StrategyBacktestEngine(Decimal("1000")).run(
        events,
        DonchianStrategy(period=2),
    )

    assert curve.equity[:3] == (
        Decimal("1000"),
        Decimal("1000"),
        Decimal("1000"),
    )
    assert curve.equity[3] == Decimal("1000") * Decimal("14") / Decimal("13")
    assert curve.drawdown[0] == Decimal("0")


def test_rejects_invalid_signal_value() -> None:
    class InvalidStrategy:
        def signals(self, events: tuple[object, ...]) -> tuple[object, ...]:
            return tuple(type("Signal", (), {"value": 2})() for _ in events)

    with pytest.raises(ValueError, match="position value"):
        StrategyBacktestEngine().run(
            (event(0), event(1)),
            InvalidStrategy(),  # type: ignore[arg-type]
        )


def test_rejects_signal_count_mismatch() -> None:
    class ShortStrategy:
        def signals(self, events: tuple[object, ...]) -> tuple[object, ...]:
            return ()

    with pytest.raises(ValueError, match="exactly one signal"):
        StrategyBacktestEngine().run(
            (event(0), event(1)),
            ShortStrategy(),  # type: ignore[arg-type]
        )


def test_rejects_boolean_signal_value() -> None:
    class BooleanStrategy:
        def signals(self, events: tuple[object, ...]) -> tuple[object, ...]:
            return tuple(type("Signal", (), {"value": True})() for _ in events)

    with pytest.raises(ValueError, match="position value"):
        StrategyBacktestEngine().run(
            (event(0), event(1)),
            BooleanStrategy(),  # type: ignore[arg-type]
        )


def test_rejects_non_position_signal() -> None:
    class MissingProtocolStrategy:
        def signals(self, events: tuple[object, ...]) -> tuple[object, ...]:
            return tuple(object() for _ in events)

    with pytest.raises(TypeError, match="PositionSignal"):
        StrategyBacktestEngine().run(
            (event(0), event(1)),
            MissingProtocolStrategy(),  # type: ignore[arg-type]
        )


def test_rejects_invalid_final_signal() -> None:
    class InvalidFinalSignalStrategy:
        def signals(self, events: tuple[object, ...]) -> tuple[object, ...]:
            return (
                type("Signal", (), {"value": 0})(),
                type("Signal", (), {"value": 2})(),
            )

    with pytest.raises(ValueError, match="position value"):
        StrategyBacktestEngine().run(
            (event(0), event(1)),
            InvalidFinalSignalStrategy(),  # type: ignore[arg-type]
        )


def test_calculates_drawdown_from_equity_peak() -> None:
    class LongStrategy:
        def signals(self, events: tuple[object, ...]) -> tuple[object, ...]:
            return tuple(type("Signal", (), {"value": 1})() for _ in events)

    curve = StrategyBacktestEngine(Decimal("100")).run(
        (
            event(0, close=10),
            event(1, close=20),
            event(2, close=10),
        ),
        LongStrategy(),  # type: ignore[arg-type]
    )

    assert curve.equity == (Decimal("100"), Decimal("200"), Decimal("100"))
    assert curve.drawdown == (Decimal("0"), Decimal("0"), Decimal("-0.5"))
