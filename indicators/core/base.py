"""FILE: indicators/core/base.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Define the typed protocol boundary shared by all indicator implementations.
LAYER: indicators
OWNS: Indicator request/output contract types and structural indicator protocol.
DOES_NOT_OWN: concrete indicator algorithms, analysis duplication, strategy, decision, risk, provider I/O
DEPENDENCIES: stdlib:dataclasses; stdlib:datetime; stdlib:typing
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import ClassVar, Mapping, Protocol, Sequence, runtime_checkable

INDICATOR_CONTRACT_ID: str = "indicator_execution_boundary"
INDICATOR_CONTRACT_VERSION: str = "1.0.0"


def _require_utc(value: datetime, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError(f"{field_name} must be timezone-aware UTC")


@dataclass(frozen=True, slots=True)
class IndicatorRequest:
    """Immutable, UTC-bounded input boundary for an indicator."""

    series: Mapping[str, Sequence[float]]
    event_time: datetime
    received_at: datetime
    source_event_id: str

    def __post_init__(self) -> None:
        if not self.source_event_id:
            raise ValueError("source_event_id must be non-empty")
        _require_utc(self.event_time, "event_time")
        _require_utc(self.received_at, "received_at")


@dataclass(frozen=True, slots=True)
class IndicatorOutput:
    """Immutable indicator result preserving the source event temporal boundary."""

    values: Mapping[str, float]
    event_time: datetime
    indicator_id: str
    contract_version: str = INDICATOR_CONTRACT_VERSION

    def __post_init__(self) -> None:
        if not self.indicator_id:
            raise ValueError("indicator_id must be non-empty")
        _require_utc(self.event_time, "event_time")


@runtime_checkable
class Indicator(Protocol):
    """Structural contract implemented by every concrete indicator."""

    contract_id: ClassVar[str] = INDICATOR_CONTRACT_ID
    contract_version: ClassVar[str] = INDICATOR_CONTRACT_VERSION
    indicator_id: ClassVar[str]

    def calculate(self, request: IndicatorRequest) -> IndicatorOutput:
        """Calculate one indicator result without provider or I/O concerns."""
        ...
