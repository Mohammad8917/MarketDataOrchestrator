"""FILE: shared/contracts/market_structure.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-30
DATE_PERSIAN: 1405-07-08
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Define the canonical market-agnostic market-structure contract and immutable structural value objects.
LAYER: shared
OWNS: Market structure input/output value semantics and structural vocabulary.
DOES_NOT_OWN: structure-detection methodology, BUY/SELL decisions, risk, execution, provider I/O, persistence
DEPENDENCIES: stdlib:dataclasses; stdlib:datetime; stdlib:decimal; stdlib:typing
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from math import isfinite
from typing import Literal, Protocol, runtime_checkable


MARKET_STRUCTURE_CONTRACT_ID = "market_structure_boundary"
MARKET_STRUCTURE_CONTRACT_VERSION = "1.0.0"

MARKET_STRUCTURE_METHODOLOGY_ID = "deterministic_confirmed_pivot_structure"
MARKET_STRUCTURE_METHODOLOGY_VERSION = "1.0.0"


@dataclass(frozen=True, slots=True)
class MarketStructureMethodology:
    """Versioned deterministic baseline methodology; descriptive only."""

    pivot_left_bars: int = 2
    pivot_right_bars: int = 2
    state_lookback: int = 10
    expansion_ratio: float = 1.25
    compression_ratio: float = 0.75

    def __post_init__(self) -> None:
        for name, value in (
            ("pivot_left_bars", self.pivot_left_bars),
            ("pivot_right_bars", self.pivot_right_bars),
            ("state_lookback", self.state_lookback),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f"{name} must be an integer >= 1")
        if isinstance(self.expansion_ratio, bool) or not isinstance(
            self.expansion_ratio, (int, float)
        ):
            raise ValueError("expansion_ratio must be numeric")
        if not isfinite(self.expansion_ratio) or not 1.0 < self.expansion_ratio:
            raise ValueError("expansion_ratio must be finite and > 1")
        if isinstance(self.compression_ratio, bool) or not isinstance(
            self.compression_ratio, (int, float)
        ):
            raise ValueError("compression_ratio must be numeric")
        if not isfinite(self.compression_ratio) or not 0.0 < self.compression_ratio < 1.0:
            raise ValueError("compression_ratio must be finite and between 0 and 1")


MARKET_STRUCTURE_METHODOLOGY = MarketStructureMethodology()

StructurePointKind = Literal["HH", "HL", "LH", "LL"]
StructureEventKind = Literal["breakout", "breakdown", "structure_shift"]
StructureStateKind = Literal["range", "expansion", "compression"]

_POINT_KINDS = frozenset(("HH", "HL", "LH", "LL"))
_EVENT_KINDS = frozenset(("breakout", "breakdown", "structure_shift"))
_STATE_KINDS = frozenset(("range", "expansion", "compression"))


def _require_utc(value: object, field_name: str) -> None:
    if not isinstance(value, datetime):
        raise ValueError(f"{field_name} must be a datetime")
    if value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
        raise ValueError(f"{field_name} must be timezone-aware UTC")


def _require_text(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must not be empty")


def _require_decimal(value: Decimal, field_name: str) -> None:
    if not isinstance(value, Decimal):
        raise TypeError(f"{field_name} must be Decimal")
    if not value.is_finite():
        raise ValueError(f"{field_name} must be finite")


@dataclass(frozen=True, slots=True)
class MarketStructureBar:
    """Normalized OHLCV observation accepted by market-structure consumers."""

    event_time: datetime
    received_at: datetime
    source_event_id: str
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal

    def __post_init__(self) -> None:
        _require_utc(self.event_time, "event_time")
        _require_utc(self.received_at, "received_at")
        _require_text(self.source_event_id, "source_event_id")
        if self.received_at < self.event_time:
            raise ValueError("received_at cannot precede event_time")

        for name in ("open", "high", "low", "close", "volume"):
            _require_decimal(getattr(self, name), name)

        if min(self.open, self.high, self.low, self.close) <= 0:
            raise ValueError("OHLC prices must be positive")
        if self.high < max(self.open, self.close, self.low):
            raise ValueError("high must be the maximum OHLC price")
        if self.low > min(self.open, self.close, self.high):
            raise ValueError("low must be the minimum OHLC price")
        if self.volume < 0:
            raise ValueError("volume must be non-negative")


@dataclass(frozen=True, slots=True)
class MarketStructureRequest:
    """Point-in-time request containing only observations available to the evaluator."""

    bars: tuple[MarketStructureBar, ...]
    event_time: datetime
    received_at: datetime
    source_event_id: str

    def __post_init__(self) -> None:
        _require_utc(self.event_time, "event_time")
        _require_utc(self.received_at, "received_at")
        _require_text(self.source_event_id, "source_event_id")
        if self.received_at < self.event_time:
            raise ValueError("received_at cannot precede event_time")
        if not self.bars:
            raise ValueError("bars must not be empty")
        if not all(isinstance(bar, MarketStructureBar) for bar in self.bars):
            raise ValueError("bars must contain only MarketStructureBar values")
        if self.bars[-1].event_time > self.event_time:
            raise ValueError("bars must not contain data after event_time")
        if any(
            current.event_time <= previous.event_time
            for previous, current in zip(self.bars, self.bars[1:])
        ):
            raise ValueError("bars must be strictly ordered by event_time")


@dataclass(frozen=True, slots=True)
class StructurePoint:
    """A structural swing label without trading direction or action semantics."""

    kind: StructurePointKind
    event_time: datetime
    source_event_id: str
    price_level: Decimal

    def __post_init__(self) -> None:
        if not isinstance(self.kind, str) or self.kind not in _POINT_KINDS:
            raise ValueError("kind must be one of HH, HL, LH, LL")
        _require_utc(self.event_time, "event_time")
        _require_text(self.source_event_id, "source_event_id")
        _require_decimal(self.price_level, "price_level")
        if self.price_level <= 0:
            raise ValueError("price_level must be positive")


@dataclass(frozen=True, slots=True)
class StructureEvent:
    """A structural event label; it never represents BUY/SELL or an order."""

    kind: StructureEventKind
    event_time: datetime
    source_event_id: str
    reference_price: Decimal

    def __post_init__(self) -> None:
        if not isinstance(self.kind, str) or self.kind not in _EVENT_KINDS:
            raise ValueError("kind must be one of breakout, breakdown, structure_shift")
        _require_utc(self.event_time, "event_time")
        _require_text(self.source_event_id, "source_event_id")
        _require_decimal(self.reference_price, "reference_price")
        if self.reference_price <= 0:
            raise ValueError("reference_price must be positive")


@dataclass(frozen=True, slots=True)
class StructureState:
    """Current descriptive structure state, not a trading signal."""

    kind: StructureStateKind
    event_time: datetime
    source_event_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.kind, str) or self.kind not in _STATE_KINDS:
            raise ValueError("kind must be one of range, expansion, compression")
        _require_utc(self.event_time, "event_time")
        _require_text(self.source_event_id, "source_event_id")


@dataclass(frozen=True, slots=True)
class MarketStructureOutput:
    """Immutable structural observation aggregate with no BUY/SELL semantics."""

    points: tuple[StructurePoint, ...]
    events: tuple[StructureEvent, ...]
    state: StructureState | None
    event_time: datetime
    source_event_id: str
    contract_version: str = MARKET_STRUCTURE_CONTRACT_VERSION

    def __post_init__(self) -> None:
        _require_utc(self.event_time, "event_time")
        _require_text(self.source_event_id, "source_event_id")
        if not isinstance(self.points, tuple):
            raise ValueError("points must be a tuple")
        if not isinstance(self.events, tuple):
            raise ValueError("events must be a tuple")
        if not all(isinstance(point, StructurePoint) for point in self.points):
            raise ValueError("points must contain only StructurePoint values")
        if not all(isinstance(event, StructureEvent) for event in self.events):
            raise ValueError("events must contain only StructureEvent values")
        if self.state is not None and not isinstance(self.state, StructureState):
            raise ValueError("state must be a StructureState when provided")
        _require_text(self.contract_version, "contract_version")
        if self.contract_version != MARKET_STRUCTURE_CONTRACT_VERSION:
            raise ValueError("unsupported contract_version")


@runtime_checkable
class MarketStructureEvaluator(Protocol):
    """Behavioral boundary; detection methodology is intentionally deferred."""

    contract_id: str
    contract_version: str

    def evaluate(self, request: MarketStructureRequest) -> MarketStructureOutput: ...
