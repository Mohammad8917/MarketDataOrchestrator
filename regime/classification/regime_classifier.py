"""FILE: regime/classification/regime_classifier.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Define and enforce the canonical regime classification boundary.
LAYER: regime
OWNS: Canonical regime classification request/output types and protocol invariants.
DOES_NOT_OWN: indicator execution, strategy execution, decision finalization, risk, provider I/O, persistence
DEPENDENCIES: stdlib:datetime; stdlib:dataclasses; stdlib:typing
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Mapping, Protocol, Sequence, runtime_checkable

REGIME_CONTRACT_ID = "regime_classification_boundary"
REGIME_CONTRACT_VERSION = "1.0.0"


def _require_utc(value: datetime, field_name: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
        raise ValueError(f"{field_name} must be timezone-aware UTC")
    return value


@dataclass(frozen=True, slots=True)
class RegimeRequest:
    features: Mapping[str, Sequence[float]]
    event_time: datetime
    received_at: datetime
    source_event_id: str

    def __post_init__(self) -> None:
        if not self.source_event_id:
            raise ValueError("source_event_id must not be empty")
        _require_utc(self.event_time, "event_time")
        _require_utc(self.received_at, "received_at")


@dataclass(frozen=True, slots=True)
class RegimeOutput:
    label: str
    confidence: float
    event_time: datetime
    regime_id: str
    contract_version: str = REGIME_CONTRACT_VERSION

    def __post_init__(self) -> None:
        if not self.label:
            raise ValueError("label must not be empty")
        if not self.regime_id:
            raise ValueError("regime_id must not be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        _require_utc(self.event_time, "event_time")


@runtime_checkable
class RegimeClassifier(Protocol):
    contract_id: str
    contract_version: str
    regime_id: str

    def classify(self, request: RegimeRequest) -> RegimeOutput: ...
