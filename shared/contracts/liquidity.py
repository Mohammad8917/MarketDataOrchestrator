"""FILE: shared/contracts/liquidity.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Define immutable point-in-time liquidity observations and deterministic liquidity-gate output.
LAYER: shared
OWNS: Typed liquidity observation and approval-boundary semantics.
DOES_NOT_OWN: market-data retrieval, depth estimation, price discovery, cost estimation, risk sizing, decision generation, or execution.
DEPENDENCIES: dataclasses, datetime
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from dataclasses import dataclass
from datetime import datetime, timezone

LIQUIDITY_CONTRACT_ID = "liquidity_evaluation_boundary"
LIQUIDITY_CONTRACT_VERSION = "1.0.0"


def _utc(value: datetime, name: str) -> None:
    if value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
        raise ValueError(f"{name} must be timezone-aware UTC")


def _nonempty(value: str, name: str) -> None:
    if not value.strip():
        raise ValueError(f"{name} must not be empty")


def _bounded(value: float, name: str) -> None:
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1")


@dataclass(frozen=True, slots=True)
class LiquidityRequest:
    available_depth_fraction: float
    required_depth_fraction: float
    requested_participation_fraction: float
    max_participation_fraction: float
    event_time: datetime
    received_at: datetime
    source_event_id: str

    def __post_init__(self) -> None:
        _utc(self.event_time, "event_time")
        _utc(self.received_at, "received_at")
        if self.received_at < self.event_time:
            raise ValueError("received_at must not precede event_time")
        _nonempty(self.source_event_id, "source_event_id")
        for name in (
            "available_depth_fraction",
            "required_depth_fraction",
            "requested_participation_fraction",
            "max_participation_fraction",
        ):
            _bounded(getattr(self, name), name)


@dataclass(frozen=True, slots=True)
class LiquidityOutput:
    approved: bool
    event_time: datetime
    liquidity_id: str
    contract_version: str = LIQUIDITY_CONTRACT_VERSION

    def __post_init__(self) -> None:
        _utc(self.event_time, "event_time")
        _nonempty(self.liquidity_id, "liquidity_id")
        if not self.contract_version:
            raise ValueError("contract_version must not be empty")
