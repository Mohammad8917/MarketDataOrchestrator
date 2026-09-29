"""FILE: regime/features/regime_features.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-29
DATE_PERSIAN: 1405-07-07
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Define the canonical boundary for normalized regime features and provenance.
LAYER: regime
OWNS: Regime feature request/output value semantics and builder protocol.
DOES_NOT_OWN: indicator algorithms, normalization methodology, strategy, decision, risk, provider I/O
DEPENDENCIES: stdlib:dataclasses; stdlib:datetime; stdlib:typing
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


REGIME_FEATURE_CONTRACT_ID = "regime_feature_construction_boundary"
REGIME_FEATURE_CONTRACT_VERSION = "1.0.0"


def _require_utc(value: datetime, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
        raise ValueError(f"{field_name} must be timezone-aware UTC")


@dataclass(frozen=True, slots=True)
class RegimeFeatureRequest:
    event_time: datetime
    received_at: datetime
    source_event_id: str
    observation_end_time: datetime

    def __post_init__(self) -> None:
        if not self.source_event_id:
            raise ValueError("source_event_id must be non-empty")
        _require_utc(self.event_time, "event_time")
        _require_utc(self.received_at, "received_at")
        _require_utc(self.observation_end_time, "observation_end_time")
        if self.observation_end_time > self.event_time:
            raise ValueError("observation_end_time must not be later than event_time")


@dataclass(frozen=True, slots=True)
class RegimeFeatureSet:
    trend_score: float
    volatility_score: float
    event_time: datetime
    source_event_id: str
    contract_version: str = REGIME_FEATURE_CONTRACT_VERSION

    def __post_init__(self) -> None:
        if not self.source_event_id:
            raise ValueError("source_event_id must be non-empty")
        _require_utc(self.event_time, "event_time")
        for name, value in (
            ("trend_score", self.trend_score),
            ("volatility_score", self.volatility_score),
        ):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"{name} must be numeric")
            if not math.isfinite(float(value)) or not -1.0 <= float(value) <= 1.0:
                raise ValueError(f"{name} must be finite and within [-1, 1]")


@runtime_checkable
class RegimeFeatureBuilder(Protocol):
    contract_id: str
    contract_version: str

    def build(self, request: RegimeFeatureRequest) -> RegimeFeatureSet: ...
