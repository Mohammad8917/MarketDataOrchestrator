"""Contract tests for the edge evaluation boundary."""

from datetime import datetime, timezone

import pytest

from shared.contracts.edge_evaluation import EdgeEvaluationOutput, EdgeEvaluationRequest


def _time() -> datetime:
    return datetime(2026, 10, 2, tzinfo=timezone.utc)


@pytest.mark.parametrize("value", ["2026-01-01T00:00:00Z", 0, None])
def test_request_rejects_invalid_event_time_runtime_types(value: object) -> None:
    with pytest.raises(ValueError, match="event_time must be a datetime"):
        EdgeEvaluationRequest(
            setup_quality=0.8,
            confirmation_strength=0.7,
            regime_alignment=0.9,
            liquidity_quality=0.8,
            cost_efficiency=0.9,
            event_time=value,  # type: ignore[arg-type]
            source_setup_id="setup-1",
            source_confirmation_id="confirmation-1",
        )


@pytest.mark.parametrize("value", ["0.5", True, None, float("nan"), float("inf")])
def test_request_rejects_invalid_numeric_runtime_types(value: object) -> None:
    with pytest.raises(ValueError, match="(must be numeric|finite and between)"):
        EdgeEvaluationRequest(
            setup_quality=value,  # type: ignore[arg-type]
            confirmation_strength=0.7,
            regime_alignment=0.9,
            liquidity_quality=0.8,
            cost_efficiency=0.9,
            event_time=_time(),
            source_setup_id="setup-1",
            source_confirmation_id="confirmation-1",
        )


@pytest.mark.parametrize("value", [0, None, object()])
def test_request_rejects_invalid_identity_runtime_types(value: object) -> None:
    with pytest.raises(ValueError, match="source_setup_id must be a string"):
        EdgeEvaluationRequest(
            setup_quality=0.8,
            confirmation_strength=0.7,
            regime_alignment=0.9,
            liquidity_quality=0.8,
            cost_efficiency=0.9,
            event_time=_time(),
            source_setup_id=value,  # type: ignore[arg-type]
            source_confirmation_id="confirmation-1",
        )


@pytest.mark.parametrize("value", ["0.5", True, None, float("nan"), float("inf")])
def test_output_rejects_invalid_edge_score_runtime_types(value: object) -> None:
    with pytest.raises(ValueError, match="(must be numeric|finite and between)"):
        EdgeEvaluationOutput(
            edge_score=value,  # type: ignore[arg-type]
            event_time=_time(),
            edge_id="edge-1",
        )


@pytest.mark.parametrize("value", [0, None, object()])
def test_output_rejects_invalid_edge_id_runtime_types(value: object) -> None:
    with pytest.raises(ValueError, match="edge_id must be a string"):
        EdgeEvaluationOutput(
            edge_score=0.7,
            event_time=_time(),
            edge_id=value,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("value", [None, 0, "", "   "])
def test_output_rejects_invalid_contract_version(value: object) -> None:
    with pytest.raises(ValueError, match="contract_version must be (a string|not be empty)"):
        EdgeEvaluationOutput(
            edge_score=0.7,
            event_time=_time(),
            edge_id="edge-1",
            contract_version=value,  # type: ignore[arg-type]
        )
