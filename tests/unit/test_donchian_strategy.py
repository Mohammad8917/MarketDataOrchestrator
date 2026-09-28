"""Tests for Donchian strategy semantics."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from shared.contracts.market_bar import MarketBar
from strategy.trend.donchian import DonchianPosition, DonchianStrategy


def bar(index: int, close: str, high: str | None = None, low: str | None = None) -> MarketBar:
    value = Decimal(close)
    return MarketBar(
        event_time=datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(hours=index),
        open=value,
        high=Decimal(high) if high is not None else value,
        low=Decimal(low) if low is not None else value,
        close=value,
        volume=Decimal("1"),
    )


def test_waits_for_full_lookback() -> None:
    events = tuple(bar(i, str(10 + i)) for i in range(3))
    assert DonchianStrategy(period=3).signals(events) == (
        DonchianPosition.FLAT,
        DonchianPosition.FLAT,
        DonchianPosition.FLAT,
    )


def test_enters_on_previous_window_upper_breakout() -> None:
    events = (
        bar(0, "10", "11", "9"),
        bar(1, "11", "12", "10"),
        bar(2, "12", "13", "11"),
        bar(3, "14", "15", "13"),
    )
    assert DonchianStrategy(period=3).signals(events)[-1] is DonchianPosition.LONG


def test_current_high_is_not_used_for_entry_threshold() -> None:
    events = (
        bar(0, "10", "11", "9"),
        bar(1, "11", "12", "10"),
        bar(2, "12", "13", "11"),
        bar(3, "12.5", "20", "12"),
    )
    assert DonchianStrategy(period=3).signals(events)[-1] is DonchianPosition.FLAT


def test_exits_below_previous_window_low() -> None:
    events = (
        bar(0, "10", "11", "9"),
        bar(1, "12", "13", "10"),
        bar(2, "14", "15", "11"),
        bar(3, "16", "17", "12"),
        bar(4, "8", "9", "7"),
    )
    assert DonchianStrategy(period=3).signals(events)[-1] is DonchianPosition.FLAT


def test_rejects_unsorted_events() -> None:
    with pytest.raises(ValueError, match="strictly ordered"):
        DonchianStrategy(period=2).signals((bar(0, "10"), bar(0, "11")))


def test_rejects_invalid_period() -> None:
    with pytest.raises(ValueError, match="at least 2"):
        DonchianStrategy(period=1)


def test_stays_long_until_exit() -> None:
    events = (
        bar(0, "10", "11", "9"),
        bar(1, "11", "12", "10"),
        bar(2, "12", "13", "11"),
        bar(3, "14", "15", "13"),
        bar(4, "15", "16", "14"),
    )
    assert DonchianStrategy(period=3).signals(events)[-1] is DonchianPosition.LONG
