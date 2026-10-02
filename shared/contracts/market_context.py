"""FILE: shared/contracts/market_context.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Define immutable market identity and point-in-time context for orchestration boundaries.
LAYER: shared
OWNS: Canonical market, symbol, timeframe, event-time, and source-event identity invariants.
DOES_NOT_OWN: provider transport, market-data retrieval, strategy methodology, analysis, risk, decision, execution, or delivery.
DEPENDENCIES: dataclasses, datetime, typing
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal

MARKET_CONTEXT_CONTRACT_ID = "market_context_boundary"
MARKET_CONTEXT_CONTRACT_VERSION = "1.0.0"
Market = Literal["Crypto", "Forex", "Gold"]


@dataclass(frozen=True, slots=True)
class MarketContext:
    """Immutable market identity aligned to one point-in-time source event."""

    market: Market
    symbol: str
    timeframe: str
    event_time: datetime
    source_event_id: str
    contract_version: str = MARKET_CONTEXT_CONTRACT_VERSION

    def __post_init__(self) -> None:
        if self.market not in {"Crypto", "Forex", "Gold"}:
            raise ValueError("market must be Crypto, Forex, or Gold")
        if not self.symbol.strip():
            raise ValueError("symbol must not be empty")
        if not self.timeframe.strip():
            raise ValueError("timeframe must not be empty")
        if self.event_time.tzinfo is None or self.event_time.utcoffset() != timezone.utc.utcoffset(
            self.event_time
        ):
            raise ValueError("event_time must be timezone-aware UTC")
        if not self.source_event_id.strip():
            raise ValueError("source_event_id must not be empty")
        if not self.contract_version.strip():
            raise ValueError("contract_version must not be empty")
