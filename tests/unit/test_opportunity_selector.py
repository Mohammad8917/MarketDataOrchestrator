"""Unit tests for deterministic opportunity selection."""

from datetime import UTC, datetime

import pytest

from analysis.opportunity_selector import OpportunitySelector
from shared.contracts.market_context import MarketContext
from shared.contracts.opportunity_ranking import OpportunityRankingOutput


NOW = datetime(2026, 1, 1, tzinfo=UTC)


def _context(*, market: str = "Crypto", symbol: str = "BTCUSDT") -> MarketContext:
    return MarketContext(market, symbol, "1h", NOW, "evt-1")  # type: ignore[arg-type]


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
        event_time=NOW,
        ranking_id=ranking_id,
        source_safety_id=f"safety-{ranking_id}",
        source_edge_id=f"edge-{ranking_id}",
    )


def test_selects_only_eligible_rankings_in_deterministic_order() -> None:
    rankings = (
        _ranking("b", 0.8),
        _ranking("a", 0.9),
        _ranking("z", 0.95, eligible=False),
    )

    result = OpportunitySelector().select(rankings, limit=2, market_context=_context())

    assert tuple(item.ranking_id for item in result.selected) == ("a", "b")
    assert all(item.eligible for item in result.selected)
    assert result.market_context.market == "Crypto"
    assert len(result.selection_id) == 64


def test_ties_are_broken_by_ranking_id() -> None:
    rankings = (_ranking("b", 0.8), _ranking("a", 0.8))

    result = OpportunitySelector().select(rankings, limit=2, market_context=_context())

    assert tuple(item.ranking_id for item in result.selected) == ("a", "b")


def test_limit_must_be_positive() -> None:
    with pytest.raises(ValueError, match="limit must be positive"):
        OpportunitySelector().select((), limit=0, market_context=_context())


def test_rejects_ranking_context_time_mismatch() -> None:
    mismatched = _ranking("x", 0.8)
    object.__setattr__(mismatched, "event_time", datetime(2026, 1, 1, 0, 0, 1, tzinfo=UTC))
    with pytest.raises(ValueError, match="ranking event_time"):
        OpportunitySelector().select((mismatched,), limit=1, market_context=_context())


def test_selection_id_is_market_context_bound() -> None:
    rankings = (_ranking("a", 0.8),)

    crypto = OpportunitySelector().select(rankings, limit=1, market_context=_context())
    forex = OpportunitySelector().select(
        rankings,
        limit=1,
        market_context=_context(market="Forex", symbol="EURUSD"),
    )

    assert crypto.selection_id != forex.selection_id
