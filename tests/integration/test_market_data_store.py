from datetime import datetime, timezone
from decimal import Decimal

from domain.common.timeframe import Timeframe
from domain.market_data_event import MarketDataEvent
from persistence.market_data_store import MarketDataStore


def make_event(offset: int = 0) -> MarketDataEvent:
    event_time = datetime(2026, 1, 1, 12, offset, tzinfo=timezone.utc)
    return MarketDataEvent.create(
        provider="binance",
        symbol="BTCUSDT",
        timeframe=Timeframe.parse("1m"),
        event_time=event_time,
        received_at=event_time,
        open=Decimal("100.10"),
        high=Decimal("101.20"),
        low=Decimal("99.90"),
        close=Decimal("100.80"),
        volume=Decimal("12.345"),
    )


def test_store_round_trips_canonical_event(tmp_path) -> None:
    event = make_event()
    with MarketDataStore(tmp_path / "market.db") as store:
        store.write(event)
        assert store.read_all() == (event,)


def test_store_is_idempotent_for_duplicate_event_id(tmp_path) -> None:
    event = make_event()
    with MarketDataStore(tmp_path / "market.db") as store:
        store.write(event)
        store.write(event)
        assert store.read_all() == (event,)


def test_store_replays_events_in_deterministic_order(tmp_path) -> None:
    later = make_event(2)
    earlier = make_event(1)
    with MarketDataStore(tmp_path / "market.db") as store:
        store.write(later)
        store.write(earlier)
        result = store.read_all()
    assert result == (earlier, later)


def test_store_rejects_non_market_data_event(tmp_path) -> None:
    with MarketDataStore(tmp_path / "market.db") as store:
        try:
            store.write(object())  # type: ignore[arg-type]
        except TypeError as exc:
            assert "MarketDataEvent" in str(exc)
        else:
            raise AssertionError("non-MarketDataEvent values must be rejected")


def test_store_context_manager_closes_connection(tmp_path) -> None:
    store = MarketDataStore(tmp_path / "market.db")
    store.close()
    try:
        store.read_all()
    except Exception as exc:
        assert "closed" in str(exc).lower()
    else:
        raise AssertionError("closed store must reject further database operations")
