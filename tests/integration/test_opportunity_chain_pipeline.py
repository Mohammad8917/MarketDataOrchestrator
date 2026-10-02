"""Integration tests for the canonical opportunity analysis chain."""

from datetime import UTC, datetime

import pytest

from analysis.opportunity_chain_pipeline import OpportunityChainPipeline
from shared.contracts.edge_evaluation import EdgeEvaluationOutput
from shared.contracts.market_context import MarketContext
from shared.contracts.pretrade_safety import PreTradeSafetyOutput
from shared.models.decision import DecisionOutput


NOW = datetime(2026, 10, 2, 12, 0, tzinfo=UTC)


def _context() -> MarketContext:
    return MarketContext("Crypto", "BTCUSDT", "1h", NOW, "evt-1")


def _decision() -> DecisionOutput:
    return DecisionOutput("BUY", 0.8, NOW, "decision-1")


def _safety(approved: bool = True) -> PreTradeSafetyOutput:
    return PreTradeSafetyOutput(
        approved,
        "BUY" if approved else "NO_TRADE",
        0.25 if approved else 0.0,
        () if approved else ("RISK_REJECTED",),
        NOW,
        "safety-1",
    )


def _edge(event_time: datetime = NOW) -> EdgeEvaluationOutput:
    return EdgeEvaluationOutput(0.6, event_time, "edge-1")


def test_chain_preserves_canonical_edge_score_and_selection_limit() -> None:
    output = OpportunityChainPipeline().evaluate(_decision(), _safety(), _edge(), 1, _context())

    assert len(output.selected) == 1
    assert output.selected[0].rank_score == 0.7
    assert output.selected[0].source_safety_id == "safety-1"
    assert output.market_context == _context()


def test_chain_preserves_safety_rejection() -> None:
    output = OpportunityChainPipeline().evaluate(
        _decision(), _safety(False), _edge(), 1, _context()
    )

    assert output.selected == ()


def test_chain_enforces_positive_selection_limit() -> None:
    with pytest.raises(ValueError, match="limit"):
        OpportunityChainPipeline().evaluate(_decision(), _safety(), _edge(), 0, _context())


def test_chain_rejects_edge_time_mismatch() -> None:
    edge = _edge(datetime(2026, 10, 2, 12, 0, 1, tzinfo=UTC))

    with pytest.raises(ValueError, match="edge and safety event_time"):
        OpportunityChainPipeline().evaluate(_decision(), _safety(), edge, 1, _context())
