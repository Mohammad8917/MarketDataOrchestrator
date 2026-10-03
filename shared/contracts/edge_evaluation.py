"""FILE: shared/contracts/edge_evaluation.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Define the immutable descriptive edge-evaluation boundary consumed by downstream opportunity ranking.
LAYER: shared
OWNS: Typed edge-evaluation request/output semantics and validation invariants.
DOES_NOT_OWN: market-data ingestion, setup/confirmation generation, cost/liquidity/risk approval, execution, persistence, probability calibration, or profitability claims.
DEPENDENCIES: dataclasses, datetime
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

import math
from dataclasses import dataclass
from datetime import datetime, timezone

EDGE_EVALUATION_CONTRACT_ID = "edge_evaluation_boundary"
EDGE_EVALUATION_CONTRACT_VERSION = "1.0.0"


def _utc(value: object, name: str) -> None:
    if not isinstance(value, datetime):
        raise ValueError(f"{name} must be a datetime")
    if value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
        raise ValueError(f"{name} must be timezone-aware UTC")


def _nonempty(value: object, name: str) -> None:
    if not isinstance(value, str):
        raise ValueError(f"{name} must be a string")
    if not value.strip():
        raise ValueError(f"{name} must not be empty")


def _bounded(value: object, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric")
    if not math.isfinite(float(value)) or not 0.0 <= float(value) <= 1.0:
        raise ValueError(f"{name} must be finite and between 0 and 1")


@dataclass(frozen=True, slots=True)
class EdgeEvaluationRequest:
    setup_quality: float
    confirmation_strength: float
    regime_alignment: float
    liquidity_quality: float
    cost_efficiency: float
    event_time: datetime
    source_setup_id: str
    source_confirmation_id: str

    def __post_init__(self) -> None:
        _utc(self.event_time, "event_time")
        for name, value in (
            ("setup_quality", self.setup_quality),
            ("confirmation_strength", self.confirmation_strength),
            ("regime_alignment", self.regime_alignment),
            ("liquidity_quality", self.liquidity_quality),
            ("cost_efficiency", self.cost_efficiency),
        ):
            _bounded(value, name)
        _nonempty(self.source_setup_id, "source_setup_id")
        _nonempty(self.source_confirmation_id, "source_confirmation_id")


@dataclass(frozen=True, slots=True)
class EdgeEvaluationOutput:
    edge_score: float
    event_time: datetime
    edge_id: str
    contract_version: str = EDGE_EVALUATION_CONTRACT_VERSION

    def __post_init__(self) -> None:
        _bounded(self.edge_score, "edge_score")
        _utc(self.event_time, "event_time")
        _nonempty(self.edge_id, "edge_id")
