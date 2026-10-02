"""FILE: shared/contracts/opportunity_ranking.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Define the immutable eligibility and ranking boundary for pre-approved opportunities.
LAYER: shared
OWNS: Typed ranking request/output semantics and validation invariants.
DOES_NOT_OWN: signal generation, cost/liquidity/risk evaluation, safety approval, execution, persistence, or profitability claims.
DEPENDENCIES: dataclasses, datetime, typing
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from dataclasses import dataclass
from datetime import datetime, timezone

OPPORTUNITY_RANKING_CONTRACT_ID = "opportunity_ranking_boundary"
OPPORTUNITY_RANKING_CONTRACT_VERSION = "1.0.0"


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
class OpportunityRankingRequest:
    safety_approved: bool
    action: str
    exposure_fraction: float
    decision_confidence: float
    edge_score: float
    event_time: datetime
    source_safety_id: str

    def __post_init__(self) -> None:
        _utc(self.event_time, "event_time")
        _nonempty(self.action, "action")
        _nonempty(self.source_safety_id, "source_safety_id")
        _bounded(self.exposure_fraction, "exposure_fraction")
        _bounded(self.decision_confidence, "decision_confidence")
        _bounded(self.edge_score, "edge_score")
        if self.safety_approved and self.action not in {"BUY", "SELL"}:
            raise ValueError("approved opportunities must be BUY or SELL")
        if not self.safety_approved and self.action != "NO_TRADE":
            raise ValueError("unapproved opportunities must be NO_TRADE")


@dataclass(frozen=True, slots=True)
class OpportunityRankingOutput:
    eligible: bool
    action: str
    rank_score: float
    event_time: datetime
    ranking_id: str
    source_safety_id: str
    contract_version: str = OPPORTUNITY_RANKING_CONTRACT_VERSION

    def __post_init__(self) -> None:
        _utc(self.event_time, "event_time")
        _nonempty(self.action, "action")
        _nonempty(self.ranking_id, "ranking_id")
        _nonempty(self.source_safety_id, "source_safety_id")
        _bounded(self.rank_score, "rank_score")
        if self.eligible and self.action not in {"BUY", "SELL"}:
            raise ValueError("eligible output must be BUY or SELL")
        if not self.eligible and self.action != "NO_TRADE":
            raise ValueError("ineligible output must be NO_TRADE")
