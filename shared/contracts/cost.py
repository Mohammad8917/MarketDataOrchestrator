"""FILE: shared/contracts/cost.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Define immutable point-in-time transaction-cost inputs and deterministic cost-gate output.
LAYER: shared
OWNS: Typed cost observation and approval-boundary semantics.
DOES_NOT_OWN: market-data retrieval, fee discovery, slippage estimation, liquidity estimation, risk sizing, decision generation, or execution.
DEPENDENCIES: dataclasses, datetime, typing
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

import math
from dataclasses import dataclass
from datetime import datetime, timezone

COST_CONTRACT_ID = "cost_evaluation_boundary"
COST_CONTRACT_VERSION = "1.0.0"


def _utc(value: object, name: str) -> None:
    if not isinstance(value, datetime):
        raise ValueError(f"{name} must be a datetime")
    if value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
        raise ValueError(f"{name} must be timezone-aware UTC")


def _nonempty(value: str, name: str) -> None:
    if not value.strip():
        raise ValueError(f"{name} must not be empty")


def _bounded(value: object, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric")
    if not math.isfinite(float(value)) or not 0.0 <= float(value) <= 1.0:
        raise ValueError(f"{name} must be finite and between 0 and 1")


@dataclass(frozen=True, slots=True)
class CostRequest:
    spread_fraction: float
    slippage_fraction: float
    fee_fraction: float
    max_cost_fraction: float
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
            "spread_fraction",
            "slippage_fraction",
            "fee_fraction",
            "max_cost_fraction",
        ):
            _bounded(getattr(self, name), name)


@dataclass(frozen=True, slots=True)
class CostOutput:
    approved: bool
    total_cost_fraction: float
    event_time: datetime
    cost_id: str
    contract_version: str = COST_CONTRACT_VERSION

    def __post_init__(self) -> None:
        _utc(self.event_time, "event_time")
        _nonempty(self.cost_id, "cost_id")
        _bounded(self.total_cost_fraction, "total_cost_fraction")
        if not self.contract_version:
            raise ValueError("contract_version must not be empty")
