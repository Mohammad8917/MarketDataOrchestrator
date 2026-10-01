"""FILE: ingestion/ingestion_service.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.2.0
DATE_GREGORIAN: 2026-10-01
DATE_PERSIAN: 1405-07-09
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Orchestrate asynchronous provider reads with isolation, bounded concurrency, timeout enforcement, and deterministic event ordering.
LAYER: ingestion
OWNS: Provider fan-in orchestration, bounded provider execution, timeout enforcement, and normalized event ordering.
DOES_NOT_OWN: Provider transport, credentials, persistence, analysis, strategy, decision, risk, retry policy.
DEPENDENCIES: stdlib:asyncio; domain.market_data_event; domain.market_data_request; ingestion.interfaces.market_provider
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

import asyncio
from collections.abc import Sequence

from domain.market_data_event import MarketDataEvent
from domain.market_data_request import MarketDataRequest
from ingestion.interfaces.market_provider import MarketDataProvider


class IngestionService:
    """Fetch independent providers with bounded concurrency and failure isolation."""

    def __init__(
        self,
        providers: Sequence[MarketDataProvider],
        *,
        concurrency: int = 4,
        timeout_seconds: float = 10.0,
    ) -> None:
        if concurrency < 1:
            raise ValueError("concurrency must be positive")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self._providers = tuple(providers)
        self._semaphore = asyncio.Semaphore(concurrency)
        self._timeout_seconds = timeout_seconds

    async def collect(
        self,
        request: MarketDataRequest,
    ) -> tuple[MarketDataEvent, ...]:
        async def fetch_one(provider: MarketDataProvider) -> tuple[MarketDataEvent, ...]:
            async with self._semaphore:
                try:
                    async with asyncio.timeout(self._timeout_seconds):
                        return await provider.fetch(request)
                except asyncio.CancelledError:
                    raise
                except Exception:
                    return ()

        results = await asyncio.gather(
            *(fetch_one(provider) for provider in self._providers),
            return_exceptions=False,
        )
        events: list[MarketDataEvent] = []
        for result in results:
            events.extend(result)
        return tuple(
            sorted(
                events,
                key=lambda event: (event.event_time, event.provider, str(event.event_id)),
            )
        )
