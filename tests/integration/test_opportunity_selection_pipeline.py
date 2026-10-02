"""Integration tests for the opportunity selection pipeline."""

from datetime import datetime, timezone

import pytest

from analysis.opportunity_selection_pipeline import OpportunitySelectionPipeline
from shared.contracts.opportunity_ranking import OpportunityRankingOutput


def _ranking(
    ranking_id: str,
    score: float,
    eligible: bool = True,
) -> OpportunityRankingOutput:
    return OpportunityRankingOutput(
        eligible=eligible,
        action="BUY" if eligible else "NO_TRADE",
        rank_score=score,
        event_time=datetime(2026, 10, 2, tzinfo=timezone.utc),
        ranking_id=ranking_id,
        source_safety_id=f"safety-{ranking_id}",
        source_edge_id=f"edge-{ranking_id}",
    )


def test_pipeline_selects_only_eligible_rankings() -> None:
    rankings = (
        _ranking("b", 0.8),
        _ranking("a", 0.9),
        _ranking("z", 0.99, eligible=False),
    )

    output = OpportunitySelectionPipeline().select(rankings, limit=2)

    assert tuple(item.ranking_id for item in output.selected) == ("a", "b")
    assert all(item.eligible for item in output.selected)


def test_pipeline_preserves_rank_scores() -> None:
    ranking = _ranking("a", 0.9)

    output = OpportunitySelectionPipeline().select((ranking,), limit=1)

    assert output.selected == (ranking,)
    assert output.selected[0].source_edge_id == "edge-a"


def test_pipeline_rejects_non_positive_limit() -> None:
    with pytest.raises(ValueError, match="limit must be positive"):
        OpportunitySelectionPipeline().select((), limit=0)
