"""Strategy-facing immutable OHLCV bar contract."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class MarketBar:
    """Validated UTC OHLCV value consumed by strategy code."""

    event_time: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal

    def __post_init__(self) -> None:
        if self.event_time.tzinfo is None or self.event_time.utcoffset() is None:
            raise ValueError("event_time must be timezone-aware")
        if self.event_time.utcoffset() != timezone.utc.utcoffset(self.event_time):
            raise ValueError("event_time must be UTC")

        values = (self.open, self.high, self.low, self.close, self.volume)
        if any(not isinstance(value, Decimal) or not value.is_finite() for value in values):
            raise ValueError("OHLCV values must be finite Decimal values")
        if min(self.open, self.high, self.low, self.close) <= 0:
            raise ValueError("OHLC prices must be positive")
        if self.high < max(self.open, self.close, self.low):
            raise ValueError("high must be the maximum OHLC price")
        if self.low > min(self.open, self.close, self.high):
            raise ValueError("low must be the minimum OHLC price")
        if self.volume < 0:
            raise ValueError("volume must be non-negative")
