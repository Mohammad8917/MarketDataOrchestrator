"""FILE: shared/interfaces/strategy.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Define the canonical typed strategy evaluation boundary shared by strategy consumers.
LAYER: shared
OWNS: Canonical strategy request/output types and protocol invariants.
DOES_NOT_OWN: indicator execution, regime classification, signal composition, decision finalization, risk, provider I/O, persistence
DEPENDENCIES: stdlib:dataclasses; stdlib:datetime; stdlib:typing
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Mapping, Protocol, runtime_checkable

STRATEGY_CONTRACT_ID = "strategy_evaluation_boundary"
STRATEGY_CONTRACT_VERSION = "1.0.0"


def _require_utc(value: datetime, field_name: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
        raise ValueError(f"{field_name} must be timezone-aware UTC")
    return value


@dataclass(frozen=True, slots=True)
class StrategyRequest:
    inputs: Mapping[str, float]
    event_time: datetime
    received_at: datetime
    source_event_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.source_event_id, str) or not self.source_event_id.strip():
            raise ValueError("source_event_id must not be empty")
        if not isinstance(self.inputs, Mapping):
            raise ValueError("inputs must be a mapping")
        if not self.inputs:
            raise ValueError("inputs must not be empty")
        _require_utc(self.event_time, "event_time")
        _require_utc(self.received_at, "received_at")
        if self.received_at < self.event_time:
            raise ValueError("received_at must not precede event_time")
        for name, value in self.inputs.items():
            if not isinstance(name, str) or not name.strip():
                raise ValueError("input names must be non-empty strings")
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError("inputs must contain only numeric values")
            if value != value or value in (float("inf"), float("-inf")):
                raise ValueError("inputs must contain only finite values")


@dataclass(frozen=True, slots=True)
class StrategyOutput:
    action: str
    strength: float
    event_time: datetime
    strategy_id: str
    contract_version: str = STRATEGY_CONTRACT_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.action, str) or not self.action.strip():
            raise ValueError("action must not be empty")
        if not isinstance(self.strategy_id, str) or not self.strategy_id.strip():
            raise ValueError("strategy_id must not be empty")
        if isinstance(self.strength, bool) or not isinstance(self.strength, (int, float)):
            raise ValueError("strength must be numeric")
        if self.strength != self.strength or self.strength in (float("inf"), float("-inf")):
            raise ValueError("strength must be finite")
        if not 0.0 <= self.strength <= 1.0:
            raise ValueError("strength must be between 0 and 1")
        _require_utc(self.event_time, "event_time")


@runtime_checkable
class Strategy(Protocol):
    contract_id: str
    contract_version: str
    strategy_id: str

    def evaluate(self, request: StrategyRequest) -> StrategyOutput: ...
