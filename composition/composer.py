"""FILE: composition/composer.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Define and enforce the canonical composition boundary for combining upstream analytical signals.
LAYER: composition
OWNS: Canonical composition request/output types and protocol invariants.
DOES_NOT_OWN: indicator execution, regime classification, strategy execution, decision finalization, risk, provider I/O, persistence
DEPENDENCIES: stdlib:dataclasses; stdlib:datetime; stdlib:typing
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Mapping, Protocol, runtime_checkable

COMPOSITION_CONTRACT_ID = "signal_composition_boundary"
COMPOSITION_CONTRACT_VERSION = "1.0.0"


def _require_utc(value: object, field_name: str) -> datetime:
    if not isinstance(value, datetime):
        raise ValueError(f"{field_name} must be a datetime")
    if value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
        raise ValueError(f"{field_name} must be timezone-aware UTC")
    return value


@dataclass(frozen=True, slots=True)
class CompositionRequest:
    signals: Mapping[str, float]
    event_time: datetime
    received_at: datetime
    source_event_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.signals, Mapping):
            raise ValueError("signals must be a mapping")
        if not self.signals:
            raise ValueError("signals must not be empty")
        if not isinstance(self.source_event_id, str) or not self.source_event_id.strip():
            raise ValueError("source_event_id must not be empty")
        _require_utc(self.event_time, "event_time")
        _require_utc(self.received_at, "received_at")
        if self.received_at < self.event_time:
            raise ValueError("received_at must not precede event_time")
        for name, value in self.signals.items():
            if not isinstance(name, str) or not name.strip():
                raise ValueError("signal names must be non-empty strings")
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError("signals must contain only numeric values")
            if not math.isfinite(float(value)):
                raise ValueError("signals must contain only finite values")


@dataclass(frozen=True, slots=True)
class CompositionOutput:
    value: float
    event_time: datetime
    composition_id: str
    contract_version: str = COMPOSITION_CONTRACT_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.contract_version, str) or not self.contract_version.strip():
            raise ValueError("contract_version must not be empty")
        if isinstance(self.value, bool) or not isinstance(self.value, (int, float)):
            raise ValueError("value must be numeric")
        if not math.isfinite(float(self.value)):
            raise ValueError("value must be finite")
        if not isinstance(self.composition_id, str) or not self.composition_id.strip():
            raise ValueError("composition_id must not be empty")
        _require_utc(self.event_time, "event_time")


@runtime_checkable
class SignalComposer(Protocol):
    contract_id: str
    contract_version: str
    composition_id: str

    def compose(self, request: CompositionRequest) -> CompositionOutput: ...
