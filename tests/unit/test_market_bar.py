"""Tests for the strategy-facing MarketBar contract."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from shared.contracts.market_bar import MarketBar


def bar(**overrides: object) -> MarketBar:
    values: dict[str, object] = {
        "event_time": datetime(2026, 1, 1, tzinfo=timezone.utc),
        "open": Decimal("10"),
        "high": Decimal("12"),
        "low": Decimal("9"),
        "close": Decimal("11"),
        "volume": Decimal("2"),
    }
    values.update(overrides)
    return MarketBar(**values)


def test_valid_bar() -> None:
    assert bar().close == Decimal("11")


def test_rejects_naive_time() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        bar(event_time=datetime(2026, 1, 1))


def test_rejects_non_utc_time() -> None:
    with pytest.raises(ValueError, match="UTC"):
        bar(event_time=datetime(2026, 1, 1, tzinfo=timezone(timedelta(hours=1))))


def test_rejects_non_decimal() -> None:
    with pytest.raises(ValueError, match="finite Decimal"):
        bar(volume=1)


def test_rejects_non_finite() -> None:
    with pytest.raises(ValueError, match="finite Decimal"):
        bar(high=Decimal("NaN"))


def test_rejects_non_positive_price() -> None:
    with pytest.raises(ValueError, match="positive"):
        bar(open=Decimal("0"))


def test_rejects_invalid_high() -> None:
    with pytest.raises(ValueError, match="maximum"):
        bar(high=Decimal("10.5"))


def test_rejects_invalid_low() -> None:
    with pytest.raises(ValueError, match="minimum"):
        bar(low=Decimal("10.5"))


def test_rejects_negative_volume() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        bar(volume=Decimal("-1"))
