from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Literal

from hypothesis import given, strategies as st

from domain.common.timeframe import Timeframe
from domain.market_data_event import MarketDataEvent


positive_decimal = st.integers(min_value=1, max_value=1_000_000).map(
    lambda value: Decimal(value) / Decimal("100")
)
identity_text = st.text(
    alphabet=st.characters(blacklist_categories=set[Literal["Cs"]]({"Cs"})),
    min_size=1,
).filter(lambda value: bool(value.strip()))


@given(
    provider=identity_text,
    symbol=identity_text,
    prices=st.lists(positive_decimal, min_size=4, max_size=4),
    volume=positive_decimal,
    minute=st.integers(min_value=0, max_value=1_000_000),
    received_seconds=st.integers(min_value=0, max_value=86_400),
)
def test_valid_market_data_event_always_satisfies_ohlc_invariants(
    provider: str,
    symbol: str,
    prices: list[Decimal],
    volume: Decimal,
    minute: int,
    received_seconds: int,
) -> None:
    event_time = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=minute)
    received_at = event_time + timedelta(seconds=received_seconds)
    open_value, _, _, close_value = prices
    expected_high = max(prices)
    expected_low = min(prices)

    event = MarketDataEvent.create(
        provider=provider,
        symbol=symbol,
        timeframe=Timeframe.parse("1m"),
        event_time=event_time,
        received_at=received_at,
        open=open_value,
        high=expected_high,
        low=expected_low,
        close=close_value,
        volume=volume,
    )

    assert event.high == expected_high
    assert event.low == expected_low
    assert event.high >= event.open
    assert event.high >= event.close
    assert event.low <= event.open
    assert event.low <= event.close
    assert event.received_at >= event.event_time
    assert event.event_id.version == 5


@given(received_seconds=st.integers(min_value=0, max_value=86_400))
def test_received_at_does_not_change_semantic_identity(received_seconds: int) -> None:
    event_time = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
    first = MarketDataEvent.create(
        provider="test-provider",
        symbol="BTC/USDT",
        timeframe=Timeframe.parse("1m"),
        event_time=event_time,
        received_at=event_time,
        open=Decimal("100"),
        high=Decimal("110"),
        low=Decimal("90"),
        close=Decimal("105"),
        volume=Decimal("12.5"),
    )
    second = MarketDataEvent.create(
        provider="test-provider",
        symbol="BTC/USDT",
        timeframe=Timeframe.parse("1m"),
        event_time=event_time,
        received_at=event_time + timedelta(seconds=received_seconds),
        open=Decimal("100"),
        high=Decimal("110"),
        low=Decimal("90"),
        close=Decimal("105"),
        volume=Decimal("12.5"),
    )

    assert first.event_id == second.event_id
