"""FILE: tests/unit/test_market_data_event.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-26
DATE_PERSIAN: 1405-07-04
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify canonical MarketDataEvent invariants and immutability.
LAYER: tests
OWNS: Unit-level acceptance tests for the domain MarketDataEvent value object.
DOES_NOT_OWN: provider transport, persistence, or higher-level business logic.
DEPENDENCIES: datetime, decimal, uuid, pytest, domain.common.timeframe, domain.market_data_event
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest

from domain.common.timeframe import Timeframe
from domain.market_data_event import MarketDataEvent


def make_market_data_event(**changes: object) -> MarketDataEvent:
    values: dict[str, object] = {
        "provider": "test-provider",
        "symbol": "BTC/USDT",
        "timeframe": Timeframe.parse("1m"),
        "event_time": datetime(2026, 9, 24, 12, 0, tzinfo=timezone.utc),
        "received_at": datetime(2026, 9, 24, 12, 0, 1, tzinfo=timezone.utc),
        "open": Decimal("100"),
        "high": Decimal("110"),
        "low": Decimal("90"),
        "close": Decimal("105"),
        "volume": Decimal("12.5"),
    }
    values.update(changes)
    return MarketDataEvent.create(**values)  # type: ignore[arg-type]


def test_known_value_is_canonical() -> None:
    event = make_market_data_event()
    assert event.symbol == "BTC/USDT"
    assert event.timeframe.code == "1m"
    assert event.high == Decimal("110")
    assert event.low == Decimal("90")


@pytest.mark.parametrize(
    "field,value",
    [
        ("provider", ""),
        ("provider", "   "),
        ("symbol", ""),
        ("symbol", "   "),
        ("event_time", datetime(2026, 9, 24, 12, 0)),
        ("received_at", datetime(2026, 9, 24, 11, 59, 59, tzinfo=timezone.utc)),
        ("open", Decimal("0")),
        ("high", Decimal("89")),
        ("low", Decimal("111")),
        ("close", Decimal("-1")),
        ("volume", Decimal("-1")),
    ],
)
def test_rejects_invalid_values(field: str, value: object) -> None:
    with pytest.raises((ValueError, TypeError)):
        make_market_data_event(**{field: value})


@pytest.mark.parametrize(
    "field,value",
    [
        ("open", Decimal("NaN")),
        ("high", Decimal("Infinity")),
        ("low", Decimal("-Infinity")),
        ("close", Decimal("NaN")),
        ("volume", Decimal("Infinity")),
    ],
)
def test_rejects_non_finite_ohlcv(field: str, value: Decimal) -> None:
    with pytest.raises(ValueError, match="finite"):
        make_market_data_event(**{field: value})


@pytest.mark.parametrize(
    "field,value",
    [
        ("open", 100),
        ("high", "110"),
        ("low", 90.0),
        ("close", object()),
        ("volume", 1),
    ],
)
def test_rejects_non_decimal_ohlcv(field: str, value: object) -> None:
    with pytest.raises(TypeError, match="Decimal"):
        make_market_data_event(**{field: value})


@pytest.mark.parametrize(
    "field,value",
    [
        ("provider", 123),
        ("symbol", object()),
    ],
)
def test_rejects_non_text_identity_fields(field: str, value: object) -> None:
    with pytest.raises(ValueError, match="non-empty string"):
        make_market_data_event(**{field: value})


def test_rejects_non_uuid_event_id() -> None:
    values = {
        "provider": "test-provider",
        "symbol": "BTC/USDT",
        "timeframe": Timeframe.parse("1m"),
        "event_time": datetime(2026, 9, 24, 12, 0, tzinfo=timezone.utc),
        "received_at": datetime(2026, 9, 24, 12, 0, 1, tzinfo=timezone.utc),
        "open": Decimal("100"),
        "high": Decimal("110"),
        "low": Decimal("90"),
        "close": Decimal("105"),
        "volume": Decimal("12.5"),
        "event_id": "not-a-uuid",
    }
    with pytest.raises(TypeError, match="event_id must be UUID"):
        MarketDataEvent(**values)  # type: ignore[arg-type]


def test_event_is_immutable() -> None:
    event = make_market_data_event()
    with pytest.raises((AttributeError, TypeError)):
        event.close = Decimal("106")  # type: ignore[misc]


def test_event_identity_is_deterministic() -> None:
    first = make_market_data_event()
    second = make_market_data_event(
        received_at=datetime(2026, 9, 24, 12, 0, 2, tzinfo=timezone.utc)
    )
    assert first.event_id == second.event_id
    assert first.event_id.version == 5


def test_event_identity_changes_when_semantic_content_changes() -> None:
    original = make_market_data_event()
    changed_close = make_market_data_event(close=Decimal("106"))
    changed_time = make_market_data_event(
        event_time=datetime(2026, 9, 24, 12, 1, tzinfo=timezone.utc),
        received_at=datetime(2026, 9, 24, 12, 1, 1, tzinfo=timezone.utc),
    )

    assert original.event_id != changed_close.event_id
    assert original.event_id != changed_time.event_id


def test_uuid4_is_rejected_as_canonical_identity() -> None:
    values = {
        "provider": "test-provider",
        "symbol": "BTC/USDT",
        "timeframe": Timeframe.parse("1m"),
        "event_time": datetime(2026, 9, 24, 12, 0, tzinfo=timezone.utc),
        "received_at": datetime(2026, 9, 24, 12, 0, 1, tzinfo=timezone.utc),
        "open": Decimal("100"),
        "high": Decimal("110"),
        "low": Decimal("90"),
        "close": Decimal("105"),
        "volume": Decimal("12.5"),
        "event_id": uuid4(),
    }
    with pytest.raises(ValueError, match="deterministic UUID5"):
        MarketDataEvent(**values)  # type: ignore[arg-type]
