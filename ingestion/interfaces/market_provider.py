"""Define the canonical asynchronous market-data provider boundary."""

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
