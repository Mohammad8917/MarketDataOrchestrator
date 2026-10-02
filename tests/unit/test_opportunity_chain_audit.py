"""Unit tests for the opportunity-chain audit adapter."""

from datetime import UTC, datetime

import pytest

from decision.opportunity_chain_audit import OpportunityChainAuditRecorder
from shared.contracts.edge_evaluation import EdgeEvaluationOutput
from shared.contracts.market_context import MarketContext
from shared.contracts.opportunity_ranking import OpportunityRankingOutput
from shared.contracts.opportunity_selection import OpportunitySelectionOutput
from shared.contracts.pretrade_safety import PreTradeSafetyOutput


NOW = datetime(2026, 10, 2, 13, tzinfo=UTC)


def _safety() -> PreTradeSafetyOutput:
    return PreTradeSafetyOutput(
        approved=True,
        action="BUY",
        exposure_fraction=0.2,
        reasons=(),
        event_time=NOW,
        safety_id="safety-1",
    )


def _chain() -> tuple[EdgeEvaluationOutput, OpportunityRankingOutput, OpportunitySelectionOutput]:
    edge = EdgeEvaluationOutput(0.7, NOW, "edge-1")
    ranking = OpportunityRankingOutput(True, "BUY", 0.75, NOW, "ranking-1", "safety-1", "edge-1")
    selection = OpportunitySelectionOutput(
        (ranking,), "selection-1", MarketContext("Crypto", "BTCUSDT", "1h", NOW, "evt-1")
    )
    return edge, ranking, selection


def test_records_complete_opportunity_chain_provenance() -> None:
    edge, ranking, selection = _chain()

    record = OpportunityChainAuditRecorder().record(
        safety=_safety(),
        decision_id="decision-1",
        cost_id="cost-1",
        liquidity_id="liquidity-1",
        risk_id="risk-1",
        edge=edge,
        ranking=ranking,
        selection=selection,
    )

    assert record.edge_id == "edge-1"
    assert record.ranking_id == "ranking-1"
    assert record.selection_id == "selection-1"
    assert record.event_time == NOW


def test_rejects_ranking_not_present_in_selection() -> None:
    edge, ranking, _ = _chain()
    other = OpportunityRankingOutput(True, "BUY", 0.8, NOW, "ranking-2", "safety-1", "edge-1")
    selection = OpportunitySelectionOutput(
        (other,), "selection-2", MarketContext("Crypto", "BTCUSDT", "1h", NOW, "evt-1")
    )

    with pytest.raises(ValueError, match="present in selection"):
        OpportunityChainAuditRecorder().record(
            safety=_safety(),
            decision_id="decision-1",
            cost_id="cost-1",
            liquidity_id="liquidity-1",
            risk_id="risk-1",
            edge=edge,
            ranking=ranking,
            selection=selection,
        )
