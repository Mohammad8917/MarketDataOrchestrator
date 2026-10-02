"""Contract tests for the opportunity ranking boundary."""

from datetime import datetime, timezone

import pytest

from shared.contracts.opportunity_ranking import (
    OpportunityRankingOutput,
    OpportunityRankingRequest,
)


def _time() -> datetime:
    return datetime(2026, 10, 2, tzinfo=timezone.utc)


def test_request_is_immutable_and_validates_approved_action() -> None:
    request = OpportunityRankingRequest(
        safety_approved=True,
        action="BUY",
        exposure_fraction=0.25,
        decision_confidence=0.8,
        edge_score=0.7,
        event_time=_time(),
        source_safety_id="safety-1",
        source_edge_id="edge-1",
    )
    assert request.action == "BUY"
    with pytest.raises((AttributeError, TypeError)):
        request.action = "SELL"  # type: ignore[misc]


def test_request_rejects_unapproved_trade_action() -> None:
    with pytest.raises(ValueError, match="unapproved opportunities"):
        OpportunityRankingRequest(
            safety_approved=False,
            action="BUY",
            exposure_fraction=0.0,
            decision_confidence=0.8,
            edge_score=0.7,
            event_time=_time(),
            source_safety_id="safety-1",
            source_edge_id="edge-1",
        )


def test_output_requires_no_trade_when_ineligible() -> None:
    with pytest.raises(ValueError, match="ineligible output"):
        OpportunityRankingOutput(
            eligible=False,
            action="WAIT",
            rank_score=0.0,
            event_time=_time(),
            ranking_id="rank-1",
            source_safety_id="safety-1",
            source_edge_id="edge-1",
        )
