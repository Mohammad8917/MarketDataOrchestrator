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


@pytest.mark.parametrize("value", ["2026-01-01T00:00:00Z", 0, None])
class _BrokenOffsetDateTime(datetime):
    def utcoffset(self) -> timedelta | None:
        raise RuntimeError("broken datetime")


def test_request_rejects_datetime_with_broken_offset() -> None:
    with pytest.raises(ValueError, match="event_time must be timezone-aware UTC"):
        OpportunityRankingRequest(
            safety_approved=True,
            action="BUY",
            exposure_fraction=0.25,
            decision_confidence=0.8,
            edge_score=0.7,
            event_time=_BrokenOffsetDateTime(2026, 1, 1, tzinfo=timezone.utc),
            source_safety_id="safety-1",
            source_edge_id="edge-1",
        )


def test_request_rejects_invalid_event_time_runtime_types(value: object) -> None:
    with pytest.raises(ValueError, match="event_time must be a datetime"):
        OpportunityRankingRequest(
            safety_approved=True,
            action="BUY",
            exposure_fraction=0.25,
            decision_confidence=0.8,
            edge_score=0.7,
            event_time=value,  # type: ignore[arg-type]
            source_safety_id="safety-1",
            source_edge_id="edge-1",
        )


@pytest.mark.parametrize("field", ["exposure_fraction", "decision_confidence", "edge_score"])
@pytest.mark.parametrize("value", [-0.01, 1.01, float("nan"), float("inf"), float("-inf")])
def test_request_rejects_out_of_range_and_non_finite_numeric_values(
    field: str, value: object
) -> None:
    values: dict[str, object] = {
        "exposure_fraction": 0.25,
        "decision_confidence": 0.8,
        "edge_score": 0.7,
    }
    values[field] = value

    with pytest.raises(ValueError, match="finite and between 0 and 1"):
        OpportunityRankingRequest(
            safety_approved=True,
            action="BUY",
            exposure_fraction=values["exposure_fraction"],  # type: ignore[arg-type]
            decision_confidence=values["decision_confidence"],  # type: ignore[arg-type]
            edge_score=values["edge_score"],  # type: ignore[arg-type]
            event_time=_time(),
            source_safety_id="safety-1",
            source_edge_id="edge-1",
        )


@pytest.mark.parametrize("value", ["0.5", True, None, float("nan"), float("inf")])
def test_request_rejects_invalid_numeric_runtime_types(value: object) -> None:
    with pytest.raises(ValueError, match="(must be numeric|finite and between)"):
        OpportunityRankingRequest(
            safety_approved=True,
            action="BUY",
            exposure_fraction=value,  # type: ignore[arg-type]
            decision_confidence=0.8,
            edge_score=0.7,
            event_time=_time(),
            source_safety_id="safety-1",
            source_edge_id="edge-1",
        )


@pytest.mark.parametrize("value", [0, None, object()])
def test_request_rejects_invalid_identity_runtime_types(value: object) -> None:
    with pytest.raises(ValueError, match="source_safety_id must be a string"):
        OpportunityRankingRequest(
            safety_approved=True,
            action="BUY",
            exposure_fraction=0.25,
            decision_confidence=0.8,
            edge_score=0.7,
            event_time=_time(),
            source_safety_id=value,  # type: ignore[arg-type]
            source_edge_id="edge-1",
        )


@pytest.mark.parametrize("value", [0, None, object()])
def test_output_rejects_invalid_identity_runtime_types(value: object) -> None:
    with pytest.raises(ValueError, match="ranking_id must be a string"):
        OpportunityRankingOutput(
            eligible=True,
            action="BUY",
            rank_score=0.7,
            event_time=_time(),
            ranking_id=value,  # type: ignore[arg-type]
            source_safety_id="safety-1",
            source_edge_id="edge-1",
        )


@pytest.mark.parametrize("value", [0, 1, 0.0, 1.0, "true", None])
def test_request_rejects_non_boolean_safety_approval(value: object) -> None:
    with pytest.raises(ValueError, match="safety_approved must be a bool"):
        OpportunityRankingRequest(
            safety_approved=value,  # type: ignore[arg-type]
            action="BUY",
            exposure_fraction=0.25,
            decision_confidence=0.8,
            edge_score=0.7,
            event_time=_time(),
            source_safety_id="safety-1",
            source_edge_id="edge-1",
        )


@pytest.mark.parametrize("value", [0, 1, 0.0, 1.0, "true", None])
def test_output_rejects_non_boolean_eligibility(value: object) -> None:
    with pytest.raises(ValueError, match="eligible must be a bool"):
        OpportunityRankingOutput(
            eligible=value,  # type: ignore[arg-type]
            action="BUY",
            rank_score=0.7,
            event_time=_time(),
            ranking_id="rank-1",
            source_safety_id="safety-1",
            source_edge_id="edge-1",
        )


@pytest.mark.parametrize("value", ["", "   ", "\t", "\n", None, 0])
def test_output_rejects_invalid_contract_version(value: object) -> None:
    with pytest.raises(ValueError, match="contract_version (must be a string|must not be empty)"):
        OpportunityRankingOutput(
            eligible=True,
            action="BUY",
            rank_score=0.7,
            event_time=_time(),
            ranking_id="rank-1",
            source_safety_id="safety-1",
            source_edge_id="edge-1",
            contract_version=value,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("version", ["2.0.0", "0.9.0", "unknown"])
def test_ranking_output_rejects_unsupported_contract_version(version: str) -> None:
    with pytest.raises(ValueError, match="unsupported contract_version"):
        OpportunityRankingOutput(
            eligible=True,
            action="BUY",
            rank_score=0.7,
            event_time=_time(),
            ranking_id="rank-1",
            source_safety_id="safety-1",
            source_edge_id="edge-1",
            contract_version=version,
        )
