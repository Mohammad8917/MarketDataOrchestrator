"""Define the canonical normalized volatility-state boundary."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol, runtime_checkable

CONTRACT_ID = "volatility_state_boundary"
CONTRACT_VERSION = "1.0.0"
METHODOLOGY_ID = "normalized_regime_volatility_passthrough"
METHODOLOGY_VERSION = "1.0.0"


def _utc(value: datetime, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
        raise ValueError(f"{field_name} must be timezone-aware UTC")


def _bounded(value: float, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric")
    if not math.isfinite(float(value)) or not -1.0 <= float(value) <= 1.0:
        raise ValueError(f"{name} must be finite and within [-1, 1]")


@dataclass(frozen=True, slots=True)
class VolatilityStateRequest:
    volatility_score: float
    event_time: datetime
    received_at: datetime
    source_event_id: str

    def __post_init__(self) -> None:
        if not self.source_event_id:
            raise ValueError("source_event_id must be non-empty")
        _utc(self.event_time, "event_time")
        _utc(self.received_at, "received_at")
        _bounded(self.volatility_score, "volatility_score")


@dataclass(frozen=True, slots=True)
class VolatilityStateOutput:
    volatility_score: float
    event_time: datetime
    source_event_id: str
    contract_version: str = CONTRACT_VERSION

    def __post_init__(self) -> None:
        if not self.source_event_id:
            raise ValueError("source_event_id must be non-empty")
        _utc(self.event_time, "event_time")
        _bounded(self.volatility_score, "volatility_score")


@runtime_checkable
class VolatilityStateEvaluator(Protocol):
    contract_id: str
    contract_version: str
    methodology_id: str
    methodology_version: str

    def assess(self, request: VolatilityStateRequest) -> VolatilityStateOutput: ...


class NormalizedRegimeVolatilityEvaluator:
    contract_id = CONTRACT_ID
    contract_version = CONTRACT_VERSION
    methodology_id = METHODOLOGY_ID
    methodology_version = METHODOLOGY_VERSION

    def assess(self, request: VolatilityStateRequest) -> VolatilityStateOutput:
        return VolatilityStateOutput(
            volatility_score=request.volatility_score,
            event_time=request.event_time,
            source_event_id=request.source_event_id,
        )
