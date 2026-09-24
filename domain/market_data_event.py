"""FILE: domain/market_data_event.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Define the canonical immutable market-data event crossing the ingestion/domain boundary.
LAYER: domain
OWNS: MarketDataEvent value semantics, temporal invariants, OHLCV invariants, and canonical event identity fields.
DOES_NOT_OWN: provider transport, provider-specific symbol aliases, persistence, indicator calculation, strategy behavior, or orchestration.
DEPENDENCIES: dataclasses, datetime, decimal, uuid, domain.common.timeframe
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from domain.common.timeframe import Timeframe


def _require_text(name: str, value: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")


def _require_utc(name: str, value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    if value.utcoffset() != timezone.utc.utcoffset(value):
        raise ValueError(f"{name} must be UTC")


def _require_decimal(name: str, value: Decimal) -> None:
    if not isinstance(value, Decimal):
        raise TypeError(f"{name} must be Decimal")
    if not value.is_finite():
        raise ValueError(f"{name} must be finite")


@dataclass(frozen=True, slots=True)
class MarketDataEvent:
    """Canonical OHLCV market-data event."""

    event_id: UUID
    provider: str
    symbol: str
    timeframe: Timeframe
    event_time: datetime
    received_at: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal

    def __post_init__(self) -> None:
        _require_text("provider", self.provider)
        _require_text("symbol", self.symbol)
        if not isinstance(self.timeframe, Timeframe):
            raise TypeError("timeframe must be Timeframe")
        if not isinstance(self.event_id, UUID):
            raise TypeError("event_id must be UUID")
        _require_utc("event_time", self.event_time)
        _require_utc("received_at", self.received_at)
        if self.received_at < self.event_time:
            raise ValueError("received_at cannot precede event_time")

        for name in ("open", "high", "low", "close", "volume"):
            _require_decimal(name, getattr(self, name))

        if min(self.open, self.high, self.low, self.close) <= 0:
            raise ValueError("OHLC prices must be positive")
        if self.high < max(self.open, self.close, self.low):
            raise ValueError("high must be the maximum OHLC price")
        if self.low > min(self.open, self.close, self.high):
            raise ValueError("low must be the minimum OHLC price")
        if self.volume < 0:
            raise ValueError("volume must be non-negative")
