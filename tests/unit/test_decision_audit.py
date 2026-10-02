"""FILE: tests/unit/test_decision_audit.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify deterministic decision-chain reconstruction metadata.
LAYER: tests
PYTHON: >=3.13
"""

from datetime import UTC, datetime

import pytest

from decision.decision_audit import DecisionAuditRecorder
from shared.contracts.edge_evaluation import EdgeEvaluationOutput
from shared.contracts.market_context import MarketContext
from shared.contracts.opportunity_ranking import OpportunityRankingOutput
from shared.contracts.opportunity_selection import OpportunitySelectionOutput
from shared.contracts.pretrade_safety import PreTradeSafetyOutput


def _safety() -> PreTradeSafetyOutput:
    return PreTradeSafetyOutput(
        approved=True,
        action="BUY",
        exposure_fraction=0.2,
        reasons=(),
        event_time=datetime(2026, 10, 2, 13, tzinfo=UTC),
        safety_id="safety-1",
    )


def test_audit_record_reconstructs_boundary_ids() -> None:
    record = DecisionAuditRecorder().record(
        _safety(),
        "decision-1",
        "cost-1",
        "liquidity-1",
        "risk-1",
    )
    assert record.decision_id == "decision-1"
    assert record.cost_id == "cost-1"
    assert record.liquidity_id == "liquidity-1"
    assert record.risk_id == "risk-1"
    assert record.safety_id == "safety-1"
    assert record.action == "BUY"


def test_audit_id_is_deterministic() -> None:
    recorder = DecisionAuditRecorder()
    first = recorder.record(_safety(), "d", "c", "l", "r")
    second = recorder.record(_safety(), "d", "c", "l", "r")
    assert first.audit_id == second.audit_id


def _opportunity_provenance() -> tuple[
    EdgeEvaluationOutput, OpportunityRankingOutput, OpportunitySelectionOutput
]:
    edge = EdgeEvaluationOutput(0.7, _safety().event_time, "edge-1")
    ranking = OpportunityRankingOutput(
        True, "BUY", 0.75, _safety().event_time, "ranking-1", "safety-1", "edge-1"
    )
    selection = OpportunitySelectionOutput(
        (ranking,),
        "selection-1",
        MarketContext("Crypto", "BTCUSDT", "1h", _safety().event_time, "evt-1"),
    )
    return edge, ranking, selection


def test_audit_records_opportunity_provenance() -> None:
    edge, ranking, selection = _opportunity_provenance()

    record = DecisionAuditRecorder().record(
        _safety(),
        "decision-1",
        "cost-1",
        "liquidity-1",
        "risk-1",
        edge=edge,
        ranking=ranking,
        selection=selection,
    )

    assert record.edge_id == "edge-1"
    assert record.ranking_id == "ranking-1"
    assert record.selection_id == "selection-1"


def test_audit_rejects_partial_opportunity_provenance() -> None:
    edge, _, _ = _opportunity_provenance()

    with pytest.raises(ValueError, match="must be supplied together"):
        DecisionAuditRecorder().record(
            _safety(),
            "d",
            "c",
            "l",
            "r",
            edge=edge,
        )


def test_audit_rejects_opportunity_time_mismatch() -> None:
    edge, ranking, selection = _opportunity_provenance()
    mismatched = EdgeEvaluationOutput(
        edge_score=edge.edge_score,
        event_time=datetime(2026, 10, 2, 13, 0, 1, tzinfo=UTC),
        edge_id=edge.edge_id,
    )

    with pytest.raises(ValueError, match="event_time"):
        DecisionAuditRecorder().record(
            _safety(),
            "d",
            "c",
            "l",
            "r",
            edge=mismatched,
            ranking=ranking,
            selection=selection,
        )
