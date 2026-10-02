"""Unit tests for deterministic opportunity ranking."""

from datetime import datetime, timezone

from analysis.opportunity_ranker import DeterministicOpportunityRanker
from shared.contracts.opportunity_ranking import OpportunityRankingRequest


def _request(
    *,
    safety_approved: bool = True,
    action: str = "BUY",
    exposure_fraction: float = 0.25,
    decision_confidence: float = 0.8,
    edge_score: float = 0.6,
) -> OpportunityRankingRequest:
    return OpportunityRankingRequest(
        safety_approved=safety_approved,
        action=action,
        exposure_fraction=exposure_fraction,
        decision_confidence=decision_confidence,
        edge_score=edge_score,
        event_time=datetime(2026, 10, 2, tzinfo=timezone.utc),
        source_safety_id="safety-1",
    )


def test_rank_is_deterministic_and_bounded() -> None:
    ranker = DeterministicOpportunityRanker()
    first = ranker.rank(_request())
    second = ranker.rank(_request())

    assert first == second
    assert first.eligible is True
    assert first.action == "BUY"
    assert first.rank_score == 0.7
    assert 0.0 <= first.rank_score <= 1.0
    assert first.source_safety_id == "safety-1"


def test_ineligible_safety_output_cannot_be_ranked_as_trade() -> None:
    request = _request(
        safety_approved=False,
        action="NO_TRADE",
        exposure_fraction=0.0,
    )

    output = DeterministicOpportunityRanker().rank(request)

    assert output.eligible is False
    assert output.action == "NO_TRADE"
    assert output.rank_score == 0.0


def test_rank_changes_with_descriptive_inputs() -> None:
    ranker = DeterministicOpportunityRanker()
    lower = ranker.rank(_request(decision_confidence=0.4, edge_score=0.2))
    higher = ranker.rank(_request(decision_confidence=0.9, edge_score=0.8))

    assert lower.rank_score < higher.rank_score
