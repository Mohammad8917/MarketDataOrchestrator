"""Adversarial contract tests for the MarketBar boundary."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from shared.contracts.market_bar import MarketBar


def _time() -> datetime:
    return datetime(2026, 10, 3, tzinfo=timezone.utc)


def _valid() -> MarketBar:
    return MarketBar(
        event_time=_time(),
        open=Decimal("100"),
        high=Decimal("110"),
        low=Decimal("90"),
        close=Decimal("105"),
        volume=Decimal("1000"),
    )


def test_market_bar_accepts_valid_data() -> None:
    assert _valid().close == Decimal("105")


@pytest.mark.parametrize(
    "value",
    [None, "2026-10-03T00:00:00Z", 1, True],
)
def test_market_bar_rejects_invalid_event_time_runtime_types(value: object) -> None:
    with pytest.raises(ValueError, match="event_time must be a datetime"):
        MarketBar(
            event_time=value,  # type: ignore[arg-type]
            open=Decimal("100"),
            high=Decimal("110"),
            low=Decimal("90"),
            close=Decimal("105"),
            volume=Decimal("1000"),
        )


def test_market_bar_rejects_naive_event_time() -> None:
    with pytest.raises(ValueError, match="event_time must be timezone-aware"):
        MarketBar(
            event_time=datetime(2026, 10, 3),
            open=Decimal("100"),
            high=Decimal("110"),
            low=Decimal("90"),
            close=Decimal("105"),
            volume=Decimal("1000"),
        )


def test_market_bar_rejects_non_utc_event_time() -> None:
    with pytest.raises(ValueError, match="event_time must be UTC"):
        MarketBar(
            event_time=datetime(2026, 10, 3, tzinfo=timezone(timedelta(hours=2))),
            open=Decimal("100"),
            high=Decimal("110"),
            low=Decimal("90"),
            close=Decimal("105"),
            volume=Decimal("1000"),
        )


@pytest.mark.parametrize(
    "field",
    ["open", "high", "low", "close", "volume"],
)
def test_market_bar_rejects_non_decimal_numeric_inputs(field: str) -> None:
    values: dict[str, object] = {
        "event_time": _time(),
        "open": Decimal("100"),
        "high": Decimal("110"),
        "low": Decimal("90"),
        "close": Decimal("105"),
        "volume": Decimal("1000"),
    }
    values[field] = 1.0
    with pytest.raises(ValueError, match="OHLCV values must be finite Decimal values"):
        MarketBar(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "value",
    [Decimal("NaN"), Decimal("Infinity"), Decimal("-Infinity")],
)
def test_market_bar_rejects_non_finite_decimal_values(value: Decimal) -> None:
    with pytest.raises(ValueError, match="OHLCV values must be finite Decimal values"):
        MarketBar(
            event_time=_time(),
            open=value,
            high=Decimal("110"),
            low=Decimal("90"),
            close=Decimal("105"),
            volume=Decimal("1000"),
        )


@pytest.mark.parametrize(
    ("high", "low", "message"),
    [
        (Decimal("104"), Decimal("90"), "high must be the maximum OHLC price"),
        (Decimal("110"), Decimal("106"), "low must be the minimum OHLC price"),
    ],
)
def test_market_bar_rejects_inconsistent_ohlc(
    high: Decimal,
    low: Decimal,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        MarketBar(
            event_time=_time(),
            open=Decimal("100"),
            high=high,
            low=low,
            close=Decimal("105"),
            volume=Decimal("1000"),
        )


@pytest.mark.parametrize(
    "field",
    ["open", "high", "low", "close"],
)
def test_market_bar_rejects_non_positive_prices(field: str) -> None:
    values: dict[str, object] = {
        "event_time": _time(),
        "open": Decimal("100"),
        "high": Decimal("110"),
        "low": Decimal("90"),
        "close": Decimal("105"),
        "volume": Decimal("1000"),
    }
    values[field] = Decimal("0")
    with pytest.raises(ValueError, match="OHLC prices must be positive"):
        MarketBar(**values)  # type: ignore[arg-type]


def test_market_bar_rejects_negative_volume() -> None:
    with pytest.raises(ValueError, match="volume must be non-negative"):
        MarketBar(
            event_time=_time(),
            open=Decimal("100"),
            high=Decimal("110"),
            low=Decimal("90"),
            close=Decimal("105"),
            volume=Decimal("-1"),
        )
