"""FILE: shared/contracts/mtf_structure.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-01
DATE_PERSIAN: 1405-07-09
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Define the canonical market-agnostic multi-timeframe market-structure alignment contract.
LAYER: shared
OWNS: Immutable multi-timeframe structure inputs, observations, alignment vocabulary, and evaluator boundary.
DOES_NOT_OWN: market-structure detection, trading decisions, risk, execution, provider I/O, persistence.
DEPENDENCIES: stdlib:dataclasses; stdlib:datetime; stdlib:typing; shared.contracts.market_structure
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal, Protocol, runtime_checkable

from shared.contracts.market_structure import MarketStructureOutput

MTF_STRUCTURE_CONTRACT_ID = "mtf_structure_alignment_boundary"
MTF_STRUCTURE_CONTRACT_VERSION = "1.0.0"
MTF_STRUCTURE_METHODOLOGY_ID = "deterministic_latest_point_alignment"
MTF_STRUCTURE_METHODOLOGY_VERSION = "1.0.0"

StructureDirection = Literal["bullish", "bearish", "unknown"]
StructureAlignment = Literal["bullish", "bearish", "mixed", "insufficient"]

_DIRECTION_VALUES = frozenset(("bullish", "bearish", "unknown"))
_ALIGNMENT_VALUES = frozenset(("bullish", "bearish", "mixed", "insufficient"))


def _require_utc(value: datetime, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
        raise ValueError(f"{field_name} must be timezone-aware UTC")


def _require_text(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must not be empty")


@dataclass(frozen=True, slots=True)
class MtfStructureInput:
    """A point-in-time structural observation for one named timeframe."""

    timeframe: str
    structure: MarketStructureOutput

    def __post_init__(self) -> None:
        _require_text(self.timeframe, "timeframe")


@dataclass(frozen=True, slots=True)
class MtfStructureRequest:
    """Point-in-time collection of independently evaluated timeframe structures."""

    inputs: tuple[MtfStructureInput, ...]
    event_time: datetime
    received_at: datetime
    source_event_id: str

    def __post_init__(self) -> None:
        _require_utc(self.event_time, "event_time")
        _require_utc(self.received_at, "received_at")
        _require_text(self.source_event_id, "source_event_id")
        if self.received_at < self.event_time:
            raise ValueError("received_at cannot precede event_time")
        if not self.inputs:
            raise ValueError("inputs must not be empty")
        names = [item.timeframe for item in self.inputs]
        if len(names) != len(set(names)):
            raise ValueError("timeframe names must be unique")
        if any(
            item.structure.event_time > self.event_time for item in self.inputs
        ):
            raise ValueError("structure observations must not contain future observations")


@dataclass(frozen=True, slots=True)
class MtfStructureObservation:
    """Descriptive directional reading for one timeframe; never a trade action."""

    timeframe: str
    direction: StructureDirection

    def __post_init__(self) -> None:
        _require_text(self.timeframe, "timeframe")
        if self.direction not in _DIRECTION_VALUES:
            raise ValueError("direction must be one of bullish, bearish, unknown")


@dataclass(frozen=True, slots=True)
class MtfStructureOutput:
    """Immutable multi-timeframe structural alignment observation."""

    observations: tuple[MtfStructureObservation, ...]
    alignment: StructureAlignment
    event_time: datetime
    source_event_id: str
    contract_version: str = MTF_STRUCTURE_CONTRACT_VERSION

    def __post_init__(self) -> None:
        _require_utc(self.event_time, "event_time")
        _require_text(self.source_event_id, "source_event_id")
        if not self.observations:
            raise ValueError("observations must not be empty")
        if self.alignment not in _ALIGNMENT_VALUES:
            raise ValueError("alignment is invalid")
        names = [item.timeframe for item in self.observations]
        if len(names) != len(set(names)):
            raise ValueError("observation timeframe names must be unique")
        if not self.contract_version:
            raise ValueError("contract_version must not be empty")


@runtime_checkable
class MtfStructureEvaluator(Protocol):
    """Behavioral boundary for deterministic multi-timeframe alignment."""

    contract_id: str
    contract_version: str

    def evaluate(self, request: MtfStructureRequest) -> MtfStructureOutput: ...
