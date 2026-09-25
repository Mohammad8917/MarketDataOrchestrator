from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from shared.contracts.market_bar import MarketBar
from strategy.trend.donchian import DonchianPosition, DonchianStrategy


def event(index: int, close: str, high: str | None = None, low: str | None = None) -> MarketBar:
    value = Decimal(close)
    high_value = Decimal(high) if high is not None else value
    low_value = Decimal(low) if low is not None else value
    timestamp = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(hours=4 * index)
    return MarketBar(
        event_time=timestamp,
        open=value,
        high=high_value,
        low=low_value,
        close=value,
        volume=Decimal("1"),
    )


def test_donchian_waits_for_full_lookback() -> None:
    events = tuple(event(index, str(index + 10)) for index in range(3))
    assert DonchianStrategy(period=3).signals(events) == (
        DonchianPosition.FLAT,
        DonchianPosition.FLAT,
        DonchianPosition.FLAT,
    )


def test_donchian_enters_only_on_breakout_of_previous_window() -> None:
    events = (
        event(0, "10", "11", "9"),
        event(1, "11", "12", "10"),
        event(2, "12", "13", "11"),
        event(3, "14", "15", "13"),
    )
    signals = DonchianStrategy(period=3).signals(events)
    assert signals[-1] is DonchianPosition.LONG


def test_donchian_does_not_use_current_high_for_entry_threshold() -> None:
    events = (
        event(0, "10", "11", "9"),
        event(1, "11", "12", "10"),
        event(2, "12", "13", "11"),
        event(3, "12.5", "20", "12"),
    )
    assert DonchianStrategy(period=3).signals(events)[-1] is DonchianPosition.FLAT


def test_donchian_exits_below_previous_window_low() -> None:
    events = (
        event(0, "10", "11", "9"),
        event(1, "12", "13", "10"),
        event(2, "14", "15", "11"),
        event(3, "16", "17", "12"),
        event(4, "8", "9", "7"),
    )
    signals = DonchianStrategy(period=3).signals(events)
    assert signals[-1] is DonchianPosition.FLAT


def test_donchian_rejects_unsorted_events() -> None:
    first = event(0, "10")
    second = event(0, "11")
    with pytest.raises(ValueError, match="strictly ordered"):
        DonchianStrategy(period=2).signals((first, second))


def test_donchian_rejects_invalid_period() -> None:
    with pytest.raises(ValueError, match="at least 2"):
        DonchianStrategy(period=1)
