"""FILE: tests/contract/test_market_data_store.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify the executable persistence consumer contract for MarketDataEvent.
LAYER: tests
OWNS: Persistence consumer contract assertions for MarketDataStore.
DOES_NOT_OWN: production persistence behavior, domain event semantics, architecture policy
DEPENDENCIES: pathlib, datetime, decimal, domain.common.timeframe, domain.market_data_event, persistence.market_data_store
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""
from datetime import datetime, timezone
from decimal import Decimal

from domain.common.timeframe import Timeframe
from domain.market_data_event import MarketDataEvent
from persistence.market_data_store import MarketDataStore


def make_event() -> MarketDataEvent:
    return MarketDataEvent.create(
        provider="demo",
        symbol="BTCUSD",
        timeframe=Timeframe.parse("1h"),
        event_time=datetime(2026, 9, 24, 12, tzinfo=timezone.utc),
        received_at=datetime(2026, 9, 24, 12, 1, tzinfo=timezone.utc),
        open=Decimal("100"),
        high=Decimal("105"),
        low=Decimal("99"),
        close=Decimal("103"),
        volume=Decimal("42.5"),
    )


def test_write_read_preserves_event(tmp_path) -> None:
    event = make_event()
    with MarketDataStore(tmp_path / "market.db") as store:
        store.write(event)
        assert store.read_all() == (event,)


def test_replay_is_idempotent_and_event_identity_is_stable(tmp_path) -> None:
    event = make_event()
    with MarketDataStore(tmp_path / "market.db") as store:
        store.write(event)
        store.write(event)
        restored = store.read_all()
    assert restored == (event,)
    assert restored[0].event_id == event.event_id


def test_decimal_and_timezone_round_trip_is_exact(tmp_path) -> None:
    event = MarketDataEvent.create(
        provider="demo",
        symbol="BTCUSD",
        timeframe=Timeframe.parse("1h"),
        event_time=datetime(2026, 9, 24, 12, 0, tzinfo=timezone.utc),
        received_at=datetime(2026, 9, 24, 12, 1, tzinfo=timezone.utc),
        open=Decimal("100.000000000000000001"),
        high=Decimal("105.123456789012345678"),
        low=Decimal("99.999999999999999999"),
        close=Decimal("103.000000000000000001"),
        volume=Decimal("42.500000000000000001"),
    )
    with MarketDataStore(tmp_path / "market.db") as store:
        store.write(event)
        restored = store.read_all()[0]
    assert restored == event
    assert restored.event_time.tzinfo is not None
    assert restored.received_at.tzinfo is not None


def test_same_identity_with_different_receive_time_does_not_duplicate(tmp_path) -> None:
    first = make_event()
    second = MarketDataEvent.create(
        provider=first.provider,
        symbol=first.symbol,
        timeframe=first.timeframe,
        event_time=first.event_time,
        received_at=datetime(2026, 9, 24, 12, 5, tzinfo=timezone.utc),
        open=first.open,
        high=first.high,
        low=first.low,
        close=first.close,
        volume=first.volume,
    )
    assert second.event_id == first.event_id
    with MarketDataStore(tmp_path / "market.db") as store:
        store.write(first)
        store.write(second)
        assert store.read_all() == (first,)
