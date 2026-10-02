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
from datetime import datetime
from typing import Literal

MARKET_CONTEXT_CONTRACT_ID = "market_context_boundary"
MARKET_CONTEXT_CONTRACT_VERSION = "1.0.0"
Market = Literal["Crypto", "Forex", "Gold"]


def _require_text(value: object, name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{name} must be a string")
    if not value.strip():
        raise ValueError(f"{name} must not be empty")
    return value


def _require_utc(value: object, name: str) -> datetime:
    if not isinstance(value, datetime):
        raise ValueError(f"{name} must be a datetime")
    offset = value.utcoffset()
    if value.tzinfo is None or offset is None or offset.total_seconds() != 0:
        raise ValueError(f"{name} must be timezone-aware UTC")
    return value


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
        if not isinstance(self.market, str) or self.market not in {"Crypto", "Forex", "Gold"}:
            raise ValueError("market must be Crypto, Forex, or Gold")
        _require_text(self.symbol, "symbol")
        _require_text(self.timeframe, "timeframe")
        _require_utc(self.event_time, "event_time")
        _require_text(self.source_event_id, "source_event_id")
        _require_text(self.contract_version, "contract_version")
