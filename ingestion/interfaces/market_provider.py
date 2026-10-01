"""FILE: ingestion/interfaces/market_provider.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-10-01
DATE_PERSIAN: 1405-07-09
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Define the canonical asynchronous market-data provider boundary over the domain request contract.
LAYER: ingestion
OWNS: Provider fetch contract and normalized market-data event boundary.
DOES_NOT_OWN: Provider transport, provider selection, persistence, strategy, backtesting, decision, risk, or order execution.
DEPENDENCIES: domain.market_data_event, domain.market_data_request
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from typing import Protocol, runtime_checkable

from domain.market_data_event import MarketDataEvent
from domain.market_data_request import MarketDataRequest


@runtime_checkable
class MarketDataProvider(Protocol):
    provider_id: str

    async def fetch(
        self,
        request: MarketDataRequest,
    ) -> tuple[MarketDataEvent, ...]:
        """Fetch normalized canonical market-data events for a domain request."""
        ...
