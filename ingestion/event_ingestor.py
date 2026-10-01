"""FILE: ingestion/event_ingestor.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-10-01
DATE_PERSIAN: 1405-07-09
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Ingest canonical market-data events from a provider through an injected persistence sink.
LAYER: ingestion
OWNS: Provider-output validation, ordering, and handoff to an injected event sink.
DOES_NOT_OWN: Provider transport, persistence implementation, strategy logic, backtesting, decision, risk, output.
DEPENDENCIES: collections.abc, domain.market_data_event, domain.market_data_request, ingestion.interfaces.market_provider
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from collections.abc import Callable

from domain.market_data_event import MarketDataEvent
from domain.market_data_request import MarketDataRequest
from ingestion.interfaces.market_provider import MarketDataProvider

EventSink = Callable[[MarketDataEvent], None]


class MarketDataIngestor:
    """Validate provider events and hand them to an injected event sink."""

    def __init__(self, sink: EventSink) -> None:
        if not callable(sink):
            raise TypeError("sink must be callable")
        self._sink = sink

    async def ingest(
        self,
        provider: MarketDataProvider,
        request: MarketDataRequest,
    ) -> tuple[MarketDataEvent, ...]:
        if not isinstance(provider, MarketDataProvider):
            raise TypeError("provider must satisfy MarketDataProvider")

        events = await provider.fetch(request)
        if not isinstance(events, tuple):
            raise TypeError("provider.fetch must return a tuple")

        previous = None
        for event in events:
            if not isinstance(event, MarketDataEvent):
                raise TypeError("provider.fetch returned a non-MarketDataEvent")
            if previous is not None and event.event_time <= previous:
                raise ValueError("provider events must be strictly increasing")
            self._sink(event)
            previous = event.event_time

        return events
