"""Canonical typed setup evaluation boundary for market-agnostic analytical setups."""

from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from typing import Literal, Mapping, Protocol, runtime_checkable

SETUP_CONTRACT_ID = "setup_evaluation_boundary"
SETUP_CONTRACT_VERSION = "1.0.0"
SetupDirection = Literal["bullish", "bearish", "neutral"]


def _require_utc(value: datetime, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
        raise ValueError(f"{field_name} must be timezone-aware UTC")


@dataclass(frozen=True, slots=True)
class SetupRequest:
    inputs: Mapping[str, float]
    event_time: datetime
    received_at: datetime
    source_event_id: str

    def __post_init__(self) -> None:
        if not self.inputs:
            raise ValueError("inputs must not be empty")
        if not self.source_event_id:
            raise ValueError("source_event_id must not be empty")
        _require_utc(self.event_time, "event_time")
        _require_utc(self.received_at, "received_at")
        if self.received_at < self.event_time:
            raise ValueError("received_at must not precede event_time")
        if any(not isfinite(value) for value in self.inputs.values()):
            raise ValueError("inputs must contain only finite values")


@dataclass(frozen=True, slots=True)
class SetupOutput:
    direction: SetupDirection
    strength: float
    event_time: datetime
    setup_id: str
    contract_version: str = SETUP_CONTRACT_VERSION

    def __post_init__(self) -> None:
        if self.direction not in {"bullish", "bearish", "neutral"}:
            raise ValueError("direction must be bullish, bearish, or neutral")
        if not self.setup_id:
            raise ValueError("setup_id must not be empty")
        if not 0.0 <= self.strength <= 1.0:
            raise ValueError("strength must be between 0 and 1")
        _require_utc(self.event_time, "event_time")


@runtime_checkable
class Setup(Protocol):
    contract_id: str
    contract_version: str
    setup_id: str

    def evaluate(self, request: SetupRequest) -> SetupOutput: ...
