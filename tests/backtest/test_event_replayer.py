"""FILE: tests/backtest/test_event_replayer.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-29
DATE_PERSIAN: 1405-07-07
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify deterministic historical MarketDataEvent replay ordering and type validation.
LAYER: tests
OWNS: EventReplayer behavioral verification.
DOES_NOT_OWN: persistence, provider transport, strategy logic, execution semantics, release approval
DEPENDENCIES: datetime, decimal, backtest.event_replayer, domain.common.timeframe, domain.market_data_event, pytest
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from backtest.event_replayer import EventReplayer
from domain.common.timeframe import Timeframe
from domain.market_data_event import MarketDataEvent


def event(index: int) -> MarketDataEvent:
    timestamp = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=index)
    return MarketDataEvent.create(
        provider="test",
        symbol="BTCUSDT",
        timeframe=Timeframe.parse("1m"),
        event_time=timestamp,
        received_at=timestamp,
        open=Decimal("10"),
        high=Decimal("11"),
        low=Decimal("9"),
        close=Decimal("10"),
        volume=Decimal("1"),
    )


def test_replays_source_unchanged_and_deterministically() -> None:
    events = (event(0), event(1), event(2))
    replayer = EventReplayer(lambda: events)

    assert replayer.replay() == events
    assert replayer.replay() == events


def test_rejects_non_tuple_source() -> None:
    with pytest.raises(TypeError, match="must return a tuple"):
        EventReplayer(lambda: [event(0), event(1)]).replay()  # type: ignore[arg-type]


def test_rejects_non_market_data_event() -> None:
    with pytest.raises(TypeError, match="non-MarketDataEvent"):
        EventReplayer(lambda: (event(0), object())).replay()  # type: ignore[arg-type]


def test_rejects_non_increasing_event_times() -> None:
    with pytest.raises(ValueError, match="strictly ordered"):
        EventReplayer(lambda: (event(1), event(1))).replay()
