"""FILE: risk/risk_engine.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Define the canonical risk evaluation boundary for risk controls and consumers.
LAYER: risk
OWNS: RiskRequest and RiskOutput contract data and validation invariants.
DOES_NOT_OWN: strategy selection, decision generation, provider I/O, persistence mutation, or output delivery.
DEPENDENCIES: stdlib:dataclasses; stdlib:datetime; typing:Mapping
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Mapping

RISK_CONTRACT_ID = "risk_evaluation_boundary"
RISK_CONTRACT_VERSION = "1.0.0"


def _utc(value: datetime, name: str) -> None:
    if value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
        raise ValueError(f"{name} must be timezone-aware UTC")


def _nonempty(value: str, name: str) -> None:
    if not value.strip():
        raise ValueError(f"{name} must not be empty")


@dataclass(frozen=True, slots=True)
class RiskRequest:
    decision_inputs: Mapping[str, float]
    event_time: datetime
    received_at: datetime
    source_event_id: str

    def __post_init__(self) -> None:
        _utc(self.event_time, "event_time")
        _utc(self.received_at, "received_at")
        _nonempty(self.source_event_id, "source_event_id")


@dataclass(frozen=True, slots=True)
class RiskOutput:
    approved: bool
    exposure_fraction: float
    event_time: datetime
    risk_id: str
    contract_version: str = RISK_CONTRACT_VERSION

    def __post_init__(self) -> None:
        _utc(self.event_time, "event_time")
        _nonempty(self.risk_id, "risk_id")
        if not 0.0 <= self.exposure_fraction <= 1.0:
            raise ValueError("exposure_fraction must be between 0 and 1")
        if not self.contract_version:
            raise ValueError("contract_version must not be empty")
