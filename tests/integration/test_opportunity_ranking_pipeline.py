"""Integration tests for the opportunity ranking pipeline."""

from datetime import datetime, timezone

import pytest

from analysis.opportunity_ranking_pipeline import OpportunityRankingPipeline
from shared.contracts.pretrade_safety import PreTradeSafetyOutput
from shared.models.decision import DecisionOutput


def _time() -> datetime:
    return datetime(2026, 10, 2, tzinfo=timezone.utc)


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
    output = OpportunityRankingPipeline().rank(_decision(), _safety(), 0.6)

    assert output.eligible is True
    assert output.action == "BUY"
    assert output.rank_score == 0.7
    assert output.source_safety_id == "safety-1"


def test_pipeline_preserves_safety_rejection() -> None:
    output = OpportunityRankingPipeline().rank(_decision(), _safety(approved=False), 1.0)

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
        OpportunityRankingPipeline().rank(decision, _safety(), 0.6)
