from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from backtest.engine import BacktestEngine, SimpleBacktestEngine
from domain.common.timeframe import Timeframe
from domain.market_data_event import MarketDataEvent


def event(close: str, offset: int) -> MarketDataEvent:
    moment = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(hours=offset)
    return MarketDataEvent.create(
        provider="test",
        symbol="BTCUSDT",
        timeframe=Timeframe.parse("1h"),
        event_time=moment,
        received_at=moment,
        open=Decimal(close),
        high=Decimal(close),
        low=Decimal(close),
        close=Decimal(close),
        volume=Decimal("1"),
    )


def test_simple_engine_implements_backtest_contract() -> None:
    assert isinstance(SimpleBacktestEngine(), BacktestEngine)


@pytest.mark.parametrize("events", [[], None, "events"])
def test_simple_engine_rejects_non_tuple_event_runtime_types(events: object) -> None:
    with pytest.raises(ValueError, match="events must be a tuple"):
        SimpleBacktestEngine().run(events)  # type: ignore[arg-type]


def test_simple_engine_rejects_invalid_event_runtime_elements() -> None:
    with pytest.raises(ValueError, match="events must contain only MarketDataEvent values"):
        SimpleBacktestEngine().run((event("100", 0), object()))  # type: ignore[arg-type]


def test_simple_engine_builds_buy_and_hold_equity_curve() -> None:
    curve = SimpleBacktestEngine().run(
        (event("100", 0), event("110", 1), event("99", 2), event("120", 3))
    )
    assert curve.equity == (
        Decimal("100"),
        Decimal("110"),
        Decimal("99"),
        Decimal("120"),
    )
    assert curve.drawdown == (
        Decimal("0"),
        Decimal("0"),
        Decimal("-0.10"),
        Decimal("0"),
    )


def test_simple_engine_tracks_drawdown_from_all_time_peak() -> None:
    curve = SimpleBacktestEngine().run(
        (
            event("100", 0),
            event("120", 1),
            event("90", 2),
            event("80", 3),
            event("110", 4),
        )
    )
    assert curve.drawdown == (
        Decimal("0"),
        Decimal("0"),
        Decimal("-0.25"),
        Decimal("-1") / Decimal("3"),
        Decimal("110") / Decimal("120") - Decimal("1"),
    )


def test_simple_engine_preserves_event_time_alignment() -> None:
    events = (event("100", 0), event("101", 1))
    curve = SimpleBacktestEngine().run(events)
    assert curve.timestamps == tuple(item.event_time for item in events)


def test_simple_engine_rejects_unsorted_events_through_output_contract() -> None:
    with pytest.raises(ValueError, match="strictly ordered by event_time"):
        SimpleBacktestEngine().run((event("101", 1), event("100", 0)))


def test_simple_engine_accepts_empty_history() -> None:
    curve = SimpleBacktestEngine().run(())
    assert curve.equity == ()
    assert curve.timestamps == ()
    assert curve.drawdown == ()


def test_simple_engine_rejects_duplicate_event_times() -> None:
    with pytest.raises(ValueError, match="strictly ordered by event_time"):
        SimpleBacktestEngine().run((event("101", 1), event("100", 1)))


def test_simple_engine_rejects_mixed_market_streams() -> None:
    gold = MarketDataEvent.create(
        provider="test",
        symbol="XAUUSD",
        timeframe=Timeframe.parse("1h"),
        event_time=datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(hours=1),
        received_at=datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(hours=1),
        open=Decimal("2000"),
        high=Decimal("2000"),
        low=Decimal("2000"),
        close=Decimal("2000"),
        volume=Decimal("1"),
    )

    with pytest.raises(ValueError, match="one provider, symbol, and timeframe stream"):
        SimpleBacktestEngine().run((event("100", 0), gold))
