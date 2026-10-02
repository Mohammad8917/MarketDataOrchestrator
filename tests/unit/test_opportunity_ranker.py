"""Unit tests for deterministic opportunity ranking."""

from datetime import datetime, timezone

from analysis.opportunity_ranker import DeterministicOpportunityRanker
from shared.contracts.opportunity_ranking import OpportunityRankingRequest


def _request(**overrides: object) -> OpportunityRankingRequest:
    values: dict[str, object] = {
        "safety_approved": True,
        "action": "BUY",
        "exposure_fraction": 0.25,
        "decision_confidence": 0.8,
        "edge_score": 0.6,
        "event_time": datetime(2026, 10, 2, tzinfo=timezone.utc),
        "source_safety_id": "safety-1",
    }
    values.update(overrides)
    return OpportunityRankingRequest(**values)


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
