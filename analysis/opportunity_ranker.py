"""FILE: analysis/opportunity_ranker.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Produce a deterministic descriptive ranking for opportunities that already passed pre-trade safety.
LAYER: analysis
OWNS: Opportunity ranking methodology and immutable ranking output construction.
DOES_NOT_OWN: signal generation, cost/liquidity/risk evaluation, safety approval, execution, persistence, or profitability claims.
DEPENDENCIES: hashlib, shared.contracts.opportunity_ranking
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from hashlib import sha256

from shared.contracts.opportunity_ranking import (
    OpportunityRankingOutput,
    OpportunityRankingRequest,
)


class DeterministicOpportunityRanker:
    """Rank only opportunities that already passed the pre-trade safety gate.

    The score is a descriptive ordering signal, not a probability or
    profitability estimate. Ineligible opportunities are never promoted.
    """

    contract_id = "opportunity_ranking_boundary"
    contract_version = "1.1.0"

    def rank(self, request: OpportunityRankingRequest) -> OpportunityRankingOutput:
        if not isinstance(request, OpportunityRankingRequest):
            raise ValueError("request must be an instance of OpportunityRankingRequest")
        eligible = request.safety_approved
        score = 0.5 * request.decision_confidence + 0.5 * request.edge_score if eligible else 0.0
        action = request.action if eligible else "NO_TRADE"
        return OpportunityRankingOutput(
            eligible=eligible,
            action=action,
            rank_score=score,
            event_time=request.event_time,
            ranking_id=self._ranking_id(request, score, eligible),
            source_safety_id=request.source_safety_id,
            source_edge_id=request.source_edge_id,
        )

    @staticmethod
    def _ranking_id(request: OpportunityRankingRequest, score: float, eligible: bool) -> str:
        payload = (
            f"{request.source_safety_id}|{request.source_edge_id}|{request.action}|"
            f"{request.decision_confidence:.12f}|{request.edge_score:.12f}|"
            f"{score:.12f}|{eligible}"
        ).encode("utf-8")
        return sha256(payload).hexdigest()
