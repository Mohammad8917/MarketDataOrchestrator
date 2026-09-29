"""FILE: tests/integration/test_ingestion_pipeline.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-29
DATE_PERSIAN: 1405-07-07
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify provider-to-store ingestion through the canonical market-data boundary.
LAYER: tests
OWNS: Integration assertions for provider output validation and persistence.
DOES_NOT_OWN: provider transport, persistence implementation, strategy logic, backtesting, or release approval.
DEPENDENCIES: asyncio, datetime, decimal, ingestion.event_ingestor, ingestion.interfaces.market_provider, persistence.market_data_store
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

import asyncio
import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Callable, cast

import pytest

from domain.common.timeframe import Timeframe
from domain.market_data_event import MarketDataEvent
from ingestion.event_ingestor import MarketDataIngestor
from ingestion.providers.binance_provider import BinanceProvider
from ingestion.interfaces.market_provider import MarketDataProvider
from persistence.market_data_store import MarketDataStore


def make_event(index: int) -> MarketDataEvent:
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


class FakeProvider:
    provider_id = "test"

    def __init__(self, events: object) -> None:
        self.events = events

    async def fetch(
        self,
        symbol: str,
        *,
        start: datetime,
        end: datetime,
    ) -> tuple[MarketDataEvent, ...]:
        return cast(tuple[MarketDataEvent, ...], self.events)


def test_ingests_provider_events_into_store(tmp_path) -> None:
    events = (make_event(0), make_event(1))

    async def scenario() -> None:
        with MarketDataStore(tmp_path / "market.db") as store:
            ingestor = MarketDataIngestor(store.write)
            result = await ingestor.ingest(
                FakeProvider(events),
                "BTCUSDT",
                start=events[0].event_time,
                end=events[-1].event_time + timedelta(minutes=1),
            )
            assert result == events
            assert store.read_all() == events

    asyncio.run(scenario())


def test_rejects_non_tuple_provider_result(tmp_path) -> None:
    event = make_event(0)

    async def scenario() -> None:
        with MarketDataStore(tmp_path / "market.db") as store:
            with pytest.raises(TypeError, match="must return a tuple"):
                await MarketDataIngestor(store.write).ingest(
                    FakeProvider(cast(object, [event])),
                    "BTCUSDT",
                    start=event.event_time,
                    end=event.event_time + timedelta(minutes=1),
                )

    asyncio.run(scenario())


def test_rejects_non_event_provider_result(tmp_path) -> None:
    event = make_event(0)

    async def scenario() -> None:
        with MarketDataStore(tmp_path / "market.db") as store:
            with pytest.raises(TypeError, match="non-MarketDataEvent"):
                await MarketDataIngestor(store.write).ingest(
                    FakeProvider(cast(object, (event, object()))),
                    "BTCUSDT",
                    start=event.event_time,
                    end=event.event_time + timedelta(minutes=1),
                )

    asyncio.run(scenario())


def test_rejects_non_increasing_provider_events(tmp_path) -> None:
    event = make_event(0)

    async def scenario() -> None:
        with MarketDataStore(tmp_path / "market.db") as store:
            with pytest.raises(ValueError, match="strictly increasing"):
                await MarketDataIngestor(store.write).ingest(
                    FakeProvider((event, event)),
                    "BTCUSDT",
                    start=event.event_time,
                    end=event.event_time + timedelta(minutes=1),
                )

    asyncio.run(scenario())


def test_rejects_invalid_store() -> None:
    with pytest.raises(TypeError, match="callable"):
        MarketDataIngestor(cast(Callable[[MarketDataEvent], None], object()))


def test_rejects_invalid_provider(tmp_path) -> None:
    event = make_event(0)

    async def scenario() -> None:
        with MarketDataStore(tmp_path / "market.db") as store:
            with pytest.raises(TypeError, match="MarketDataProvider"):
                await MarketDataIngestor(store.write).ingest(
                    cast(MarketDataProvider, object()),
                    "BTCUSDT",
                    start=event.event_time,
                    end=event.event_time + timedelta(minutes=1),
                )

    asyncio.run(scenario())



class BinanceResponse:
    def __init__(self, payload: object) -> None:
        self._payload = payload

    def __enter__(self) -> "BinanceResponse":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self._payload).encode()


def test_ingests_binance_provider_output_into_store(tmp_path) -> None:
    rows = [
        [1767225600000, "100", "110", "90", "105", "12.5", 1767239999999, "0", 1, "0", "0", "0"],
        [1767240000000, "105", "115", "100", "112", "13.5", 1767254399999, "0", 1, "0", "0", "0"],
    ]

    def opener(request, *, timeout):
        return BinanceResponse(rows)

    async def scenario() -> None:
        provider = BinanceProvider(interval="4h", limit=2, opener=opener)
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        end = datetime(2026, 1, 2, tzinfo=timezone.utc)
        with MarketDataStore(tmp_path / "market.db") as store:
            result = await MarketDataIngestor(store.write).ingest(
                provider, "btcusdt", start=start, end=end
            )
            assert len(result) == 2
            assert result[0].provider == "binance"
            assert result[0].symbol == "BTCUSDT"
            assert store.read_all() == result

    asyncio.run(scenario())
