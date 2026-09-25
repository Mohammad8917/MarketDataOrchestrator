"""Tests for Donchian strategy."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from domain.common.timeframe import Timeframe
from domain.market_data_event import MarketDataEvent
from shared.contracts.market_bar import MarketBar
from strategy.trend.donchian import DonchianPosition, DonchianStrategy


def make_event(
    close: Decimal,
    high: Decimal | None = None,
    low: Decimal | None = None,
    timestamp_offset: int = 0,
) -> MarketBar:
    """Create a strategy-facing MarketBar from a canonical fake MarketDataEvent."""
    high_value = high if high is not None else close
    low_value = low if low is not None else close
    timestamp = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(hours=4 * timestamp_offset)
    event = MarketDataEvent.create(
        provider="test",
        symbol="BTCUSDT",
        timeframe=Timeframe.parse("4h"),
        event_time=timestamp,
        received_at=timestamp,
        open=close,
        high=high_value,
        low=low_value,
        close=close,
        volume=Decimal("1"),
    )
    return MarketBar(
        event_time=event.event_time,
        open=event.open,
        high=event.high,
        low=event.low,
        close=event.close,
        volume=event.volume,
    )


def test_hold_when_insufficient_data() -> None:
    """With fewer than period candles, signal is HOLD."""
    strategy = DonchianStrategy(period=20)
    events = (make_event(close=Decimal("100"), timestamp_offset=0),)
    result = strategy.signals(events)
    assert result[-1] is DonchianPosition.FLAT


def test_buy_on_upper_breakout() -> None:
    """Price above the previous upper channel triggers LONG."""
    strategy = DonchianStrategy(period=20)
    events = tuple(
        make_event(
            close=Decimal("100"),
            high=Decimal("110"),
            low=Decimal("90"),
            timestamp_offset=index,
        )
        for index in range(20)
    ) + (
        make_event(
            close=Decimal("111"),
            high=Decimal("112"),
            low=Decimal("109"),
            timestamp_offset=20,
        ),
    )
    assert strategy.signals(events)[-1] is DonchianPosition.LONG


def test_sell_on_lower_breakout() -> None:
    """A close below the previous lower channel exits the LONG position."""
    strategy = DonchianStrategy(period=20)
    events = tuple(
        make_event(
            close=Decimal("100"),
            high=Decimal("110"),
            low=Decimal("90"),
            timestamp_offset=index,
        )
        for index in range(20)
    ) + (
        make_event(
            close=Decimal("111"),
            high=Decimal("112"),
            low=Decimal("109"),
            timestamp_offset=20,
        ),
        make_event(
            close=Decimal("89"),
            high=Decimal("91"),
            low=Decimal("88"),
            timestamp_offset=21,
        ),
    )
    assert strategy.signals(events)[-1] is DonchianPosition.FLAT


def test_hold_inside_channel() -> None:
    """A close inside the previous channel produces HOLD."""
    strategy = DonchianStrategy(period=20)
    events = tuple(
        make_event(
            close=Decimal("100"),
            high=Decimal("110"),
            low=Decimal("90"),
            timestamp_offset=index,
        )
        for index in range(20)
    ) + (
        make_event(
            close=Decimal("100"),
            high=Decimal("105"),
            low=Decimal("95"),
            timestamp_offset=20,
        ),
    )
    assert strategy.signals(events)[-1] is DonchianPosition.FLAT


def test_invalid_period_raises() -> None:
    """period < 2 raises ValueError."""
    with pytest.raises(ValueError):
        DonchianStrategy(period=1)
