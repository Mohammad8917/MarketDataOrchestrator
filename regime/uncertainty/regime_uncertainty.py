"""FILE: regime/uncertainty/regime_uncertainty.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-30
DATE_PERSIAN: 1405-07-08
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Define and evaluate the canonical normalized regime-uncertainty boundary.
LAYER: regime
OWNS: Regime uncertainty request/output contracts and the confidence-complement baseline evaluator.
DOES_NOT_OWN: market-data transport, provider I/O, persistence, strategy, risk, or decision finalization
DEPENDENCIES: dataclasses, datetime, math, typing
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

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
        if self.received_at < self.event_time:
            raise ValueError("received_at must not precede event_time")
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

    def assess(self, request: RegimeUncertaintyRequest) -> RegimeUncertaintyOutput: ...


class ConfidenceComplementUncertaintyEvaluator:
    contract_id = CONTRACT_ID
    contract_version = CONTRACT_VERSION
    methodology_id = METHODOLOGY_ID
    methodology_version = METHODOLOGY_VERSION

    def assess(self, request: RegimeUncertaintyRequest) -> RegimeUncertaintyOutput:
        return RegimeUncertaintyOutput(
            uncertainty_score=1.0 - request.confidence,
            event_time=request.event_time,
            source_event_id=request.source_event_id,
        )
