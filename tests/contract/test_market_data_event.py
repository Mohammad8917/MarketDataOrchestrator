"""Contract tests for canonical MarketDataEvent invariants."""

from datetime import datetime, timedelta, timezone, tzinfo
from decimal import Decimal
from typing import Any, cast
from uuid import uuid4

import pytest

from domain.common.timeframe import Timeframe
from domain.market_data_event import MarketDataEvent


class _NoOffsetTZ(tzinfo):
    def utcoffset(self, dt):
        return None

    def dst(self, dt):
        return None

    def tzname(self, dt):
        return "NO_OFFSET"


def valid_kwargs() -> dict[str, object]:
    return {
        "event_id": MarketDataEvent.derive_event_id(
            provider="demo",
            symbol="BTCUSD",
            timeframe=Timeframe.parse("1h"),
            event_time=datetime(2026, 9, 24, 12, tzinfo=timezone.utc),
            open=Decimal("100"),
            high=Decimal("105"),
            low=Decimal("99"),
            close=Decimal("103"),
            volume=Decimal("42.5"),
        ),
        "provider": "demo",
        "symbol": "BTCUSD",
        "timeframe": Timeframe.parse("1h"),
        "event_time": datetime(2026, 9, 24, 12, tzinfo=timezone.utc),
        "received_at": datetime(2026, 9, 24, 12, 1, tzinfo=timezone.utc),
        "open": Decimal("100"),
        "high": Decimal("105"),
        "low": Decimal("99"),
        "close": Decimal("103"),
        "volume": Decimal("42.5"),
    }


def make_event(**overrides: object) -> MarketDataEvent:
    values: dict[str, Any] = valid_kwargs()
    values.update(overrides)
    return MarketDataEvent(**cast(dict[str, Any], values))


def test_create_derives_replay_stable_identity() -> None:
    event = make_event()
    recreated = MarketDataEvent.create(
        provider=event.provider,
        symbol=event.symbol,
        timeframe=event.timeframe,
        event_time=event.event_time,
        received_at=event.received_at,
        open=event.open,
        high=event.high,
        low=event.low,
        close=event.close,
        volume=event.volume,
    )
    assert recreated == event
    assert recreated.event_id.version == 5


@pytest.mark.parametrize("field", ["provider", "symbol"])
def test_text_fields_must_be_non_empty_strings(field: str) -> None:
    with pytest.raises(ValueError):
        make_event(**{field: ""})
    with pytest.raises(ValueError):
        make_event(**{field: "   "})
    with pytest.raises(ValueError):
        make_event(**{field: 123})


def test_utc_validation_rejects_naive_and_non_utc_datetimes() -> None:
    with pytest.raises(ValueError):
        make_event(event_time=datetime(2026, 9, 24, 12))
    with pytest.raises(ValueError):
        make_event(event_time=datetime(2026, 9, 24, 12, tzinfo=timezone(timedelta(hours=3))))


def test_utc_validation_rejects_timezone_without_offset() -> None:
    with pytest.raises(ValueError):
        make_event(event_time=datetime(2026, 9, 24, 12, tzinfo=_NoOffsetTZ()))


def test_decimal_validation_rejects_wrong_type_and_non_finite_values() -> None:
    with pytest.raises(TypeError):
        make_event(open=100)
    with pytest.raises(ValueError):
        make_event(open=Decimal("NaN"))


def test_identity_and_timeframe_types_are_strict() -> None:
    with pytest.raises(TypeError):
        make_event(timeframe="1h")
    with pytest.raises(TypeError):
        make_event(event_id="not-a-uuid")
    with pytest.raises(ValueError):
        make_event(event_id=uuid4())


def test_received_at_cannot_precede_event_time() -> None:
    with pytest.raises(ValueError):
        make_event(received_at=datetime(2026, 9, 24, 11, 59, tzinfo=timezone.utc))


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("open", Decimal("0")),
        ("high", Decimal("98")),
        ("low", Decimal("104")),
        ("volume", Decimal("-1")),
    ],
)
def test_ohlcv_invariants_reject_invalid_values(field: str, value: Decimal) -> None:
    with pytest.raises(ValueError):
        make_event(**{field: value})


def test_ohlcv_invariants_accept_valid_values() -> None:
    event = make_event()
    assert min(event.open, event.high, event.low, event.close) > 0
    assert event.high >= max(event.open, event.close, event.low)
    assert event.low <= min(event.open, event.close, event.high)
    assert event.volume >= 0
