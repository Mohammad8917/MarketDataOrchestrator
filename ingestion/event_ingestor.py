"""FILE: ingestion/event_ingestor.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-29
DATE_PERSIAN: 1405-07-07
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Ingest canonical market-data events from a provider through an injected persistence sink.
LAYER: ingestion
OWNS: Provider-output validation, ordering, and handoff to an injected event sink.
DOES_NOT_OWN: provider transport, persistence implementation, strategy logic, backtesting, decision, risk, output.
DEPENDENCIES: datetime, collections.abc, domain.market_data_event, ingestion.interfaces.market_provider
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from domain.market_data_event import MarketDataEvent
from ingestion.interfaces.market_provider import MarketDataProvider

EventSink = Callable[[MarketDataEvent], None]


class MarketDataIngestor:
    """Validate provider events and hand them to an injected persistence sink."""

    def __init__(self, sink: EventSink) -> None:
        if not callable(sink):
            raise TypeError("sink must be callable")
        self._sink = sink

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
            self._sink(event)
            previous = event.event_time

        return events
