"""FILE: ingestion/event_ingestor.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-29
DATE_PERSIAN: 1405-07-07
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Ingest canonical market-data events from a provider into persistent storage.
LAYER: ingestion
OWNS: Provider-to-store ingestion orchestration and ordering/type validation.
DOES_NOT_OWN: provider transport, persistence implementation, strategy logic, backtesting, decision, risk, output.
DEPENDENCIES: datetime, ingestion.interfaces.market_provider, domain.market_data_event, persistence.market_data_store
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from datetime import datetime

from domain.market_data_event import MarketDataEvent
from ingestion.interfaces.market_provider import MarketDataProvider
from persistence.market_data_store import MarketDataStore


class MarketDataIngestor:
    """Persist a validated provider result as canonical market-data events."""

    def __init__(self, store: MarketDataStore) -> None:
        if not isinstance(store, MarketDataStore):
            raise TypeError("store must be a MarketDataStore")
        self._store = store

    async def ingest(
        self,
        provider: MarketDataProvider,
        symbol: str,
        *,
        start: datetime,
        end: datetime,
    ) -> tuple[MarketDataEvent, ...]:
        if not isinstance(provider, MarketDataProvider):
            raise TypeError("provider must satisfy MarketDataProvider")

        events = await provider.fetch(symbol, start=start, end=end)
        if not isinstance(events, tuple):
            raise TypeError("provider.fetch must return a tuple")

        previous: datetime | None = None
        for event in events:
            if not isinstance(event, MarketDataEvent):
                raise TypeError("provider.fetch returned a non-MarketDataEvent")
            if previous is not None and event.event_time <= previous:
                raise ValueError("provider events must be strictly increasing")
            self._store.write(event)
            previous = event.event_time

        return events
