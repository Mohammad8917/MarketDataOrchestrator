"""Integration tests for the opportunity selection pipeline."""

from datetime import UTC, datetime

import pytest

from analysis.opportunity_selection_pipeline import OpportunitySelectionPipeline
from shared.contracts.market_context import MarketContext
from shared.contracts.opportunity_ranking import OpportunityRankingOutput
from shared.contracts.opportunity_selection import OPPORTUNITY_SELECTION_CONTRACT_VERSION


NOW = datetime(2026, 10, 2, tzinfo=UTC)
CONTEXT = MarketContext("Crypto", "BTCUSDT", "1h", NOW, "evt-1")


def _ranking(
    ranking_id: str,
    score: float,
    eligible: bool = True,
) -> OpportunityRankingOutput:
    return OpportunityRankingOutput(
        eligible=eligible,
        action="BUY" if eligible else "NO_TRADE",
        rank_score=score,
        event_time=NOW,
        ranking_id=ranking_id,
        source_safety_id=f"safety-{ranking_id}",
        source_edge_id=f"edge-{ranking_id}",
    )


def test_pipeline_contract_version_tracks_canonical_contract() -> None:
    assert OpportunitySelectionPipeline.contract_version == OPPORTUNITY_SELECTION_CONTRACT_VERSION


def test_pipeline_selects_only_eligible_rankings() -> None:
    rankings = (
        _ranking("b", 0.8),
        _ranking("a", 0.9),
        _ranking("z", 0.99, eligible=False),
    )

    output = OpportunitySelectionPipeline().select(rankings, limit=2, market_context=CONTEXT)

    assert tuple(item.ranking_id for item in output.selected) == ("a", "b")
    assert all(item.eligible for item in output.selected)
    assert output.market_context == CONTEXT


def test_pipeline_preserves_rank_scores() -> None:
    ranking = _ranking("a", 0.9)

    output = OpportunitySelectionPipeline().select((ranking,), limit=1, market_context=CONTEXT)

    assert output.selected == (ranking,)
    assert output.selected[0].source_edge_id == "edge-a"


def test_pipeline_rejects_non_positive_limit() -> None:
    with pytest.raises(ValueError, match="limit must be positive"):
        OpportunitySelectionPipeline().select((), limit=0, market_context=CONTEXT)


@pytest.mark.parametrize("field", ["rankings", "market_context"])
def test_pipeline_rejects_wrong_runtime_boundary_types(field: str) -> None:
    values = {"rankings": (_ranking("a", 0.8),), "market_context": CONTEXT}
    values[field] = None  # type: ignore[assignment]
    with pytest.raises(ValueError, match=field):
        OpportunitySelectionPipeline().select(**values, limit=1)  # type: ignore[arg-type]


@pytest.mark.parametrize("limit", [True, False, 1.0, "1", None])
def test_pipeline_rejects_invalid_limit_runtime_types(limit: object) -> None:
    with pytest.raises(ValueError, match="positive integer"):
        OpportunitySelectionPipeline().select((), limit=limit, market_context=CONTEXT)  # type: ignore[arg-type]
