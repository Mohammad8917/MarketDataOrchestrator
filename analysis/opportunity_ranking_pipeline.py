"""FILE: analysis/opportunity_ranking_pipeline.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Integrate canonical Decision, PreTradeSafety, and OpportunityRanking boundaries.
LAYER: analysis
OWNS: Boundary adaptation only; no analytical recalculation.
DOES_NOT_OWN: signal generation, cost/liquidity/risk evaluation, safety approval, persistence, execution, or ranking methodology.
DEPENDENCIES: analysis.opportunity_ranker, shared.contracts.opportunity_ranking, shared.contracts.pretrade_safety, shared.models.decision
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from shared.contracts.opportunity_ranking import (
    OpportunityRankingOutput,
    OpportunityRankingRequest,
)
from shared.contracts.pretrade_safety import PreTradeSafetyOutput
from shared.models.decision import DecisionOutput

from analysis.opportunity_ranker import DeterministicOpportunityRanker


class OpportunityRankingPipeline:
    """Adapt completed canonical boundaries into the ranking contract."""

    contract_id = "opportunity_ranking_boundary"
    contract_version = "1.0.0"

    def __init__(self, ranker: DeterministicOpportunityRanker | None = None) -> None:
        self._ranker = ranker or DeterministicOpportunityRanker()

    def rank(
        self,
        decision: DecisionOutput,
        safety: PreTradeSafetyOutput,
        edge_score: float,
    ) -> OpportunityRankingOutput:
        """Rank only after the canonical pre-trade safety result exists."""
        if safety.event_time != decision.event_time:
            raise ValueError("decision and safety event_time must match")
        request = OpportunityRankingRequest(
            safety_approved=safety.approved,
            action=safety.action,
            exposure_fraction=safety.exposure_fraction,
            decision_confidence=decision.confidence,
            edge_score=edge_score,
            event_time=safety.event_time,
            source_safety_id=safety.safety_id,
        )
        return self._ranker.rank(request)
