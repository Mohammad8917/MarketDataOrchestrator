from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol, runtime_checkable

CONTRACT_ID = "regime_uncertainty_boundary"
CONTRACT_VERSION = "1.0.0"
METHODOLOGY_ID = "confidence_complement_baseline"
METHODOLOGY_VERSION = "1.0.0"


def _utc(value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
        raise ValueError("timestamp must be timezone-aware UTC")


def _bounded(value: float, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric")
    if not math.isfinite(float(value)) or not 0.0 <= float(value) <= 1.0:
        raise ValueError(f"{name} must be finite and within [0, 1]")


@dataclass(frozen=True, slots=True)
class RegimeUncertaintyRequest:
    confidence: float
    event_time: datetime
    received_at: datetime
    source_event_id: str

    def __post_init__(self) -> None:
        if not self.source_event_id:
            raise ValueError("source_event_id must be non-empty")
        _utc(self.event_time)
        _utc(self.received_at)
        _bounded(self.confidence, "confidence")


@dataclass(frozen=True, slots=True)
class RegimeUncertaintyOutput:
    uncertainty_score: float
    event_time: datetime
    source_event_id: str
    contract_version: str = CONTRACT_VERSION

    def __post_init__(self) -> None:
        if not self.source_event_id:
            raise ValueError("source_event_id must be non-empty")
        _utc(self.event_time)
        _bounded(self.uncertainty_score, "uncertainty_score")


@runtime_checkable
class RegimeUncertaintyEvaluator(Protocol):
    contract_id: str
    contract_version: str
    methodology_id: str
    methodology_version: str

    def assess(
        self, request: RegimeUncertaintyRequest
    ) -> RegimeUncertaintyOutput: ...
