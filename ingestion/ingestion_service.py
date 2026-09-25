"""FILE: ingestion/ingestion_service.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Orchestrate asynchronous provider reads with isolation, bounded concurrency, timeout enforcement, and deterministic event ordering.
LAYER: ingestion
OWNS: Provider fan-in orchestration, bounded provider execution, timeout enforcement, and normalized event ordering.
DOES_NOT_OWN: Provider transport, credentials, persistence, analysis, strategy, decision, risk, retry policy.
DEPENDENCIES: stdlib:asyncio; stdlib:datetime; ingestion.interfaces.market_provider
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

import asyncio
from collections.abc import Sequence
from datetime import datetime, timezone

from ingestion.interfaces.market_provider import MarketDataProvider, MarketEvent


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
        symbol: str,
        *,
        start: datetime,
        end: datetime,
    ) -> tuple[MarketEvent, ...]:
        if not symbol.strip():
            raise ValueError("symbol must be non-empty")
        self._validate_utc(start, "start")
        self._validate_utc(end, "end")
        if start >= end:
            raise ValueError("start must be before end")

        async def fetch_one(provider: MarketDataProvider) -> tuple[MarketEvent, ...]:
            async with self._semaphore:
                try:
                    async with asyncio.timeout(self._timeout_seconds):
                        return await provider.fetch(symbol, start=start, end=end)
                except asyncio.CancelledError:
                    raise
                except Exception:
                    return ()

        results = await asyncio.gather(
            *(fetch_one(provider) for provider in self._providers),
            return_exceptions=False,
        )
        events: list[MarketEvent] = []
        for result in results:
            events.extend(result)
        return tuple(
            sorted(
                events,
                key=lambda event: (event.event_time, event.source, event.source_event_id),
            )
        )

    @staticmethod
    def _validate_utc(value: datetime, field_name: str) -> None:
        if value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
            raise ValueError(f"{field_name} must be timezone-aware UTC")
