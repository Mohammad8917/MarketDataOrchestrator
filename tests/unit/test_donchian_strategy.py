"""FILE: tests/unit/test_donchian_strategy.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-29
DATE_PERSIAN: 1405-07-07
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify deterministic Donchian strategy signals over historical MarketBar values.
LAYER: tests
OWNS: Verification of the test_donchian_strategy test contract and behavior.
DOES_NOT_OWN: Production implementation, runtime orchestration, or release approval.
DEPENDENCIES: shared.contracts.market_bar; strategy.trend.donchian; pytest
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

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
        make_bar(2, high=13, low=9, close=13),
    )
    assert DonchianStrategy(period=2).signals(events)[-1] is DonchianPosition.LONG


def test_long_position_exits_below_prior_lower_channel() -> None:
    events = (
        make_bar(0, high=10, low=8, close=9),
        make_bar(1, high=11, low=8, close=10),
        make_bar(2, high=14, low=9, close=14),
        make_bar(3, high=10, low=6, close=7),
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
