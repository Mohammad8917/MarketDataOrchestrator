"""FILE: tests/unit/test_donchian_engine.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify point-in-time Donchian strategy backtest execution and no-lookahead behavior.
LAYER: tests
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from backtest.donchian_engine import DonchianBacktestEngine
from domain.common.timeframe import Timeframe
from domain.market_data_event import MarketDataEvent


def event(index: int, *, high: int, low: int, close: int) -> MarketDataEvent:
    moment = datetime(2026, 1, 1, tzinfo=UTC) + timedelta(minutes=index)
    return MarketDataEvent.create(
        provider="test",
        symbol="BTCUSDT",
        timeframe=Timeframe.parse("1m"),
        event_time=moment,
        received_at=moment,
        open=Decimal(str(close)),
        high=Decimal(str(high)),
        low=Decimal(str(low)),
        close=Decimal(str(close)),
        volume=Decimal("1"),
    )


def test_donchian_backtest_applies_signal_on_next_bar() -> None:
    events = (
        event(0, high=10, low=8, close=9),
        event(1, high=11, low=8, close=10),
        event(2, high=13, low=9, close=13),
        event(3, high=14, low=10, close=14),
    )

    result = DonchianBacktestEngine(period=2).run(events)

    assert result.equity == (
        Decimal("1"),
        Decimal("1"),
        Decimal("1"),
        Decimal("14") / Decimal("13"),
    )


def test_donchian_backtest_does_not_use_current_close_to_enter() -> None:
    events = (
        event(0, high=10, low=8, close=9),
        event(1, high=11, low=8, close=10),
        event(2, high=13, low=9, close=13),
    )

    result = DonchianBacktestEngine(period=2).run(events)

    assert result.equity[-1] == Decimal("1")


def test_donchian_backtest_derives_drawdown_from_equity() -> None:
    events = (
        event(0, high=10, low=8, close=9),
        event(1, high=11, low=8, close=10),
        event(2, high=13, low=9, close=13),
        event(3, high=14, low=10, close=14),
        event(4, high=11, low=6, close=7),
    )

    result = DonchianBacktestEngine(period=2).run(events)

    assert result.equity[-1] == Decimal("7") / Decimal("13")
    assert result.drawdown[-1] == Decimal("-0.5")


def test_donchian_backtest_rejects_invalid_input() -> None:
    with pytest.raises(ValueError, match="events must not be empty"):
        DonchianBacktestEngine(period=2).run(())

    with pytest.raises(ValueError, match="strictly ordered"):
        DonchianBacktestEngine(period=2).run(
            (
                event(1, high=10, low=8, close=9),
                event(1, high=11, low=8, close=10),
            )
        )

    with pytest.raises(ValueError, match="initial_equity"):
        DonchianBacktestEngine(initial_equity=Decimal("0"))
