"""FILE: ingestion/interfaces/market_provider.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-27
DATE_PERSIAN: 1405-07-05
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Define the canonical asynchronous market-data provider boundary.
LAYER: ingestion
OWNS: Provider fetch contract and normalized market-data event boundary.
DOES_NOT_OWN: Provider transport, persistence, strategy, backtesting, decision, risk, or order execution.
DEPENDENCIES: datetime, typing, domain.market_data_event
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime
from typing import Protocol, runtime_checkable

from domain.market_data_event import MarketDataEvent


@runtime_checkable
class MarketDataProvider(Protocol):
    provider_id: str

    async def fetch(
        self,
        symbol: str,
        *,
        start: datetime,
        end: datetime,
    ) -> tuple[MarketDataEvent, ...]:
        """Fetch normalized canonical market-data events."""
        ...
