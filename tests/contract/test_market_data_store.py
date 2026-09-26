"""FILE: tests/contract/test_market_data_store.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-26
DATE_PERSIAN: 1405-07-04
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
from typing import cast

import pytest

from domain.common.timeframe import Timeframe
from domain.market_data_event import MarketDataEvent
from persistence.market_data_store import MarketDataStore


def make_event(
    *,
    event_time: datetime | None = None,
    received_at: datetime | None = None,
) -> MarketDataEvent:
    event_time = event_time or datetime(2026, 9, 24, 12, tzinfo=timezone.utc)
    received_at = received_at or datetime(2026, 9, 24, 12, 1, tzinfo=timezone.utc)
    return MarketDataEvent.create(
        provider="demo",
        symbol="BTCUSD",
        timeframe=Timeframe.parse("1h"),
        event_time=event_time,
        received_at=received_at,
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


def test_same_identity_with_different_receive_time_does_not_duplicate(
    tmp_path,
) -> None:
    first = make_event()
    second = make_event(
        received_at=datetime(2026, 9, 24, 12, 5, tzinfo=timezone.utc)
    )
    assert second.event_id == first.event_id
    with MarketDataStore(tmp_path / "market.db") as store:
        store.write(first)
        store.write(second)
        assert store.read_all() == (first,)


def test_write_rejects_non_event(tmp_path) -> None:
    with MarketDataStore(tmp_path / "market.db") as store:
        with pytest.raises(TypeError, match="event must be a MarketDataEvent"):
            store.write(cast(MarketDataEvent, object()))


def test_parse_utc_rejects_naive_stored_datetime() -> None:
    with pytest.raises(ValueError, match="stored datetime must be timezone-aware"):
        MarketDataStore._parse_utc("2026-09-24T12:00:00")


def test_parse_utc_normalizes_offset_aware_storage_to_utc() -> None:
    parsed = MarketDataStore._parse_utc("2026-09-24T15:00:00+03:00")
    assert parsed == datetime(2026, 9, 24, 12, tzinfo=timezone.utc)


def test_read_all_orders_by_event_time_then_identity(tmp_path) -> None:
    first = make_event(
        event_time=datetime(2026, 9, 24, 13, tzinfo=timezone.utc),
        received_at=datetime(2026, 9, 24, 13, 1, tzinfo=timezone.utc),
    )
    second = make_event(
        event_time=datetime(2026, 9, 24, 12, tzinfo=timezone.utc),
        received_at=datetime(2026, 9, 24, 12, 1, tzinfo=timezone.utc),
    )
    with MarketDataStore(tmp_path / "market.db") as store:
        store.write(first)
        store.write(second)
        assert store.read_all() == (second, first)
