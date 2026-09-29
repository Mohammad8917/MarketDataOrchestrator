"""Tests for the Donchian historical strategy."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from shared.contracts.market_bar import MarketBar
from strategy.trend.donchian import DonchianPosition, DonchianStrategy


def make_bar(index: int, *, high: int = 12, low: int = 8, close: int = 10) -> MarketBar:
    return MarketBar(
        event_time=datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=index),
        open=Decimal("10"),
        high=Decimal(str(high)),
        low=Decimal(str(low)),
        close=Decimal(str(close)),
        volume=Decimal("1"),
    )


def test_period_must_be_at_least_two() -> None:
    with pytest.raises(ValueError, match="at least 2"):
        DonchianStrategy(period=1)


def test_warmup_is_flat() -> None:
    events = tuple(make_bar(i) for i in range(3))
    assert DonchianStrategy(period=3).signals(events) == (
        DonchianPosition.FLAT,
        DonchianPosition.FLAT,
        DonchianPosition.FLAT,
    )


def test_breakout_uses_prior_bars_only() -> None:
    events = (
        make_bar(0, high=10, low=8, close=9),
        make_bar(1, high=11, low=8, close=10),
        make_bar(2, high=12, low=9, close=13),
    )
    assert DonchianStrategy(period=2).signals(events)[-1] is DonchianPosition.LONG


def test_long_position_exits_below_prior_lower_channel() -> None:
    events = (
        make_bar(0, high=10, low=8, close=9),
        make_bar(1, high=11, low=8, close=10),
        make_bar(2, high=13, low=9, close=14),
        make_bar(3, high=12, low=10, close=9),
    )
    assert DonchianStrategy(period=2).signals(events) == (
        DonchianPosition.FLAT,
        DonchianPosition.FLAT,
        DonchianPosition.LONG,
        DonchianPosition.FLAT,
    )


def test_order_must_be_strict() -> None:
    events = (make_bar(1), make_bar(1))
    with pytest.raises(ValueError, match="strictly ordered"):
        DonchianStrategy(period=2).signals(events)
