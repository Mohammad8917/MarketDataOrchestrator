"""FILE: ingestion/interfaces/market_provider.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.2.0
DATE_GREGORIAN: 2026-09-25
DATE_PERSIAN: 1405-07-03
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Define the canonical asynchronous market-data provider boundary.
LAYER: ingestion
OWNS: Canonical market-data provider interface.
DOES_NOT_OWN: Concrete exchange transport, retries, credentials, persistence, analysis, strategy, decision, risk.
DEPENDENCIES: stdlib:datetime, domain.market_data_event
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol, runtime_checkable

from domain.market_data_event import MarketDataEvent


@dataclass(frozen=True, slots=True)
class MarketEvent:
    source_event_id: str
    source: str
    symbol: str
    event_time: datetime
    received_at: datetime
    payload_digest: str

    def __post_init__(self) -> None:
        if not self.source_event_id.strip() or not self.source.strip() or not self.symbol.strip():
            raise ValueError("market event identity fields must be non-empty")
        if self.event_time.tzinfo is None or self.event_time.utcoffset() != timezone.utc.utcoffset(
            self.event_time
        ):
            raise ValueError("event_time must be timezone-aware UTC")
        if (
            self.received_at.tzinfo is None
            or self.received_at.utcoffset() != timezone.utc.utcoffset(self.received_at)
        ):
            raise ValueError("received_at must be timezone-aware UTC")
        if not self.payload_digest.strip():
            raise ValueError("payload_digest must be non-empty")


@runtime_checkable
class MarketDataProvider(Protocol):
    provider_id: str

    async def fetch(
        self,
        symbol: str,
        *,
        start: datetime | None = None,
        end: datetime | None = None,
        interval: str | None = None,
        limit: int | None = None,
    ) -> tuple[MarketDataEvent, ...]:
        """Fetch normalized canonical market-data events."""
        ...
