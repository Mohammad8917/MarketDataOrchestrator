"""FILE: domain/market_data_request.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-01
DATE_PERSIAN: 1405-07-09
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Define the immutable market-data acquisition request crossing the domain/ingestion boundary.
LAYER: domain
OWNS: Market scope, symbol, timeframe, and UTC time-window request semantics.
DOES_NOT_OWN: provider transport, provider selection, persistence, analysis, strategy, risk, execution, or orchestration.
DEPENDENCIES: dataclasses, datetime, domain.common.timeframe, domain.market_scope
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from dataclasses import dataclass
from datetime import datetime, timezone

from domain.common.timeframe import Timeframe
from domain.market_scope import MarketScope


CONTRACT_ID = "market_data_request_boundary"
CONTRACT_VERSION = "1.0.0"


def _require_utc(name: str, value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
        raise ValueError(f"{name} must be timezone-aware UTC")


def _require_text(name: str, value: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")


@dataclass(frozen=True, slots=True)
class MarketDataRequest:
    """Immutable, provider-neutral request for canonical market data."""

    market: MarketScope
    symbol: str
    timeframe: Timeframe
    start: datetime
    end: datetime
    contract_version: str = CONTRACT_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.market, MarketScope):
            raise TypeError("market must be MarketScope")
        _require_text("symbol", self.symbol)
        if not isinstance(self.timeframe, Timeframe):
            raise TypeError("timeframe must be Timeframe")
        _require_utc("start", self.start)
        _require_utc("end", self.end)
        if self.start >= self.end:
            raise ValueError("start must be before end")
        if self.contract_version != CONTRACT_VERSION:
            raise ValueError(f"contract_version must be {CONTRACT_VERSION}")
