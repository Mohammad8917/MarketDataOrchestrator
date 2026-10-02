"""Deterministic, market-agnostic opportunity ranking methodology."""

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
    contract_version = "1.0.0"

    def rank(self, request: OpportunityRankingRequest) -> OpportunityRankingOutput:
        eligible = request.safety_approved
        score = (
            0.5 * request.decision_confidence
            + 0.5 * request.edge_score
            if eligible
            else 0.0
        )
        action = request.action if eligible else "NO_TRADE"
        return OpportunityRankingOutput(
            eligible=eligible,
            action=action,
            rank_score=score,
            event_time=request.event_time,
            ranking_id=self._ranking_id(request, score, eligible),
            source_safety_id=request.source_safety_id,
        )

    @staticmethod
    def _ranking_id(
        request: OpportunityRankingRequest, score: float, eligible: bool
    ) -> str:
        payload = (
            f"{request.source_safety_id}|{request.action}|"
            f"{request.decision_confidence:.12f}|{request.edge_score:.12f}|"
            f"{score:.12f}|{eligible}"
        ).encode("utf-8")
        return sha256(payload).hexdigest()
