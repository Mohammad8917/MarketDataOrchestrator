"""Integration tests for the opportunity ranking pipeline."""

from datetime import datetime, timezone

import pytest

from analysis.opportunity_ranking_pipeline import OpportunityRankingPipeline
from shared.contracts.edge_evaluation import EdgeEvaluationOutput
from shared.contracts.pretrade_safety import PreTradeSafetyOutput
from shared.models.decision import DecisionOutput


def _time() -> datetime:
    return datetime(2026, 10, 2, tzinfo=timezone.utc)


def _edge() -> EdgeEvaluationOutput:
    return EdgeEvaluationOutput(edge_score=0.6, event_time=_time(), edge_id="edge-1")


def _decision() -> DecisionOutput:
    return DecisionOutput(
        action="BUY",
        confidence=0.8,
        event_time=_time(),
        decision_id="decision-1",
    )


def _safety(approved: bool = True) -> PreTradeSafetyOutput:
    return PreTradeSafetyOutput(
        approved=approved,
        action="BUY" if approved else "NO_TRADE",
        exposure_fraction=0.25 if approved else 0.0,
        reasons=() if approved else ("RISK_REJECTED",),
        event_time=_time(),
        safety_id="safety-1",
    )


def test_pipeline_consumes_canonical_boundaries() -> None:
    output = OpportunityRankingPipeline().rank(_decision(), _safety(), _edge())

    assert output.eligible is True
    assert output.action == "BUY"
    assert output.rank_score == 0.7
    assert output.source_safety_id == "safety-1"


def test_pipeline_preserves_safety_rejection() -> None:
    output = OpportunityRankingPipeline().rank(_decision(), _safety(approved=False), _edge())

    assert output.eligible is False
    assert output.action == "NO_TRADE"
    assert output.rank_score == 0.0


def test_pipeline_rejects_temporal_mismatch() -> None:
    decision = DecisionOutput(
        action="BUY",
        confidence=0.8,
        event_time=datetime(2026, 10, 2, 0, 0, 1, tzinfo=timezone.utc),
        decision_id="decision-1",
    )

    with pytest.raises(ValueError, match="event_time"):
        OpportunityRankingPipeline().rank(decision, _safety(), _edge())


def test_pipeline_rejects_edge_temporal_mismatch() -> None:
    edge = EdgeEvaluationOutput(
        edge_score=0.6,
        event_time=datetime(2026, 10, 2, 0, 0, 1, tzinfo=timezone.utc),
        edge_id="edge-1",
    )

    with pytest.raises(ValueError, match="edge and safety event_time"):
        OpportunityRankingPipeline().rank(_decision(), _safety(), edge)


@pytest.mark.parametrize("field", ["decision", "safety", "edge"])
def test_pipeline_rejects_wrong_runtime_boundary_types(field: str) -> None:
    values = {"decision": _decision(), "safety": _safety(), "edge": _edge()}
    values[field] = None  # type: ignore[assignment]
    with pytest.raises(ValueError, match=field):
        OpportunityRankingPipeline().rank(**values)  # type: ignore[arg-type]



def test_pipeline_contract_version_tracks_canonical_contract() -> None:
    from shared.contracts.opportunity_ranking import OPPORTUNITY_RANKING_CONTRACT_VERSION

    assert OpportunityRankingPipeline.contract_version == OPPORTUNITY_RANKING_CONTRACT_VERSION
