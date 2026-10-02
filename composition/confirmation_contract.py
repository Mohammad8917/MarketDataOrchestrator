"""FILE: composition/confirmation_contract.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-01
DATE_PERSIAN: 1405-07-09
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Define the executable boundary for market-agnostic analytical confirmation.
LAYER: composition
OWNS: Immutable confirmation request/output and confirmation contract semantics.
DOES_NOT_OWN: signal generation, market-data I/O, persistence, risk, cost, decision finalization, trading actions
DEPENDENCIES: None
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from typing import Mapping, Protocol, runtime_checkable

CONFIRMATION_CONTRACT_ID = "signal_confirmation_boundary"
CONFIRMATION_CONTRACT_VERSION = "1.0.0"


def _require_utc(value: datetime, field_name: str) -> None:
    offset = value.utcoffset()
    if value.tzinfo is None or offset is None:
        raise ValueError(f"{field_name} must be timezone-aware")
    if offset.total_seconds() != 0:
        raise ValueError(f"{field_name} must be UTC")


@dataclass(frozen=True, slots=True)
class ConfirmationRequest:
    signals: Mapping[str, float]
    event_time: datetime
    received_at: datetime
    source_event_id: str

    def __post_init__(self) -> None:
        if not self.source_event_id.strip():
            raise ValueError("source_event_id must not be empty")
        _require_utc(self.event_time, "event_time")
        _require_utc(self.received_at, "received_at")
        if self.received_at < self.event_time:
            raise ValueError("received_at must not precede event_time")
        for name, value in self.signals.items():
            if not name.strip():
                raise ValueError("signal names must not be empty")
            if not isfinite(value):
                raise ValueError("signals must contain only finite values")


@dataclass(frozen=True, slots=True)
class ConfirmationOutput:
    confirmed: bool
    score: float
    event_time: datetime
    confirmation_id: str
    contract_version: str = CONFIRMATION_CONTRACT_VERSION

    def __post_init__(self) -> None:
        if not self.confirmation_id.strip():
            raise ValueError("confirmation_id must not be empty")
        if not isfinite(self.score) or not -1.0 <= self.score <= 1.0:
            raise ValueError("score must be finite and within [-1.0, 1.0]")
        _require_utc(self.event_time, "event_time")


@runtime_checkable
class SignalConfirmation(Protocol):
    contract_id: str
    contract_version: str
    confirmation_id: str

    def confirm(self, request: ConfirmationRequest) -> ConfirmationOutput: ...
