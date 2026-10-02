"""Unit tests for deterministic opportunity selection."""

from datetime import datetime, timezone

import pytest

from analysis.opportunity_selector import OpportunitySelector
from shared.contracts.opportunity_ranking import OpportunityRankingOutput


def _ranking(
    ranking_id: str,
    score: float,
    eligible: bool = True,
    action: str = "BUY",
) -> OpportunityRankingOutput:
    return OpportunityRankingOutput(
        eligible=eligible,
        action=action if eligible else "NO_TRADE",
        rank_score=score,
        event_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
        ranking_id=ranking_id,
        source_safety_id=f"safety-{ranking_id}",
    )


def test_selects_only_eligible_rankings_in_deterministic_order() -> None:
    rankings = (
        _ranking("b", 0.8),
        _ranking("a", 0.9),
        _ranking("z", 0.95, eligible=False),
    )

    result = OpportunitySelector().select(rankings, limit=2)

    assert tuple(item.ranking_id for item in result.selected) == ("a", "b")
    assert all(item.eligible for item in result.selected)


def test_ties_are_broken_by_ranking_id() -> None:
    rankings = (
        _ranking("b", 0.8),
        _ranking("a", 0.8),
    )

    result = OpportunitySelector().select(rankings, limit=2)

    assert tuple(item.ranking_id for item in result.selected) == ("a", "b")


def test_limit_must_be_positive() -> None:
    with pytest.raises(ValueError, match="limit must be positive"):
        OpportunitySelector().select((), limit=0)


def test_contract_rejects_ineligible_selection() -> None:
    with pytest.raises(ValueError, match="selection may contain eligible opportunities only"):
        from shared.contracts.opportunity_selection import OpportunitySelectionOutput

        OpportunitySelectionOutput(
            selected=(_ranking("x", 0.0, eligible=False),),
        )


def test_contract_rejects_ascending_scores() -> None:
    with pytest.raises(ValueError, match="ordered by rank_score"):
        from shared.contracts.opportunity_selection import OpportunitySelectionOutput

        OpportunitySelectionOutput(
            selected=(_ranking("a", 0.7), _ranking("b", 0.8)),
        )
