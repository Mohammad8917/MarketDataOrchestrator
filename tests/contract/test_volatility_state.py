from datetime import datetime, timezone

import pytest

from volatility.state.volatility_state import (
    CONTRACT_ID,
    CONTRACT_VERSION,
    METHODOLOGY_ID,
    METHODOLOGY_VERSION,
    NormalizedRegimeVolatilityEvaluator,
    VolatilityStateOutput,
    VolatilityStateRequest,
)

EVENT_TIME = datetime(2026, 1, 1, tzinfo=timezone.utc)


def make_request(score: float = 0.25) -> VolatilityStateRequest:
    return VolatilityStateRequest(
        volatility_score=score,
        event_time=EVENT_TIME,
        received_at=EVENT_TIME,
        source_event_id="event-1",
    )


def test_contract_identity() -> None:
    evaluator = NormalizedRegimeVolatilityEvaluator()
    assert evaluator.contract_id == CONTRACT_ID
    assert evaluator.contract_version == CONTRACT_VERSION
    assert evaluator.methodology_id == METHODOLOGY_ID
    assert evaluator.methodology_version == METHODOLOGY_VERSION


def test_assess_preserves_score_and_provenance() -> None:
    result = NormalizedRegimeVolatilityEvaluator().assess(make_request(-0.5))
    assert result == VolatilityStateOutput(
        volatility_score=-0.5,
        event_time=EVENT_TIME,
        source_event_id="event-1",
    )


@pytest.mark.parametrize("score", [-1.0, 0.0, 1.0])
def test_boundary_scores_are_valid(score: float) -> None:
    assert make_request(score).volatility_score == score


@pytest.mark.parametrize("score", [-1.0001, 1.0001, float("inf"), float("-inf"), float("nan")])
def test_invalid_scores_fail(score: float) -> None:
    with pytest.raises(ValueError):
        make_request(score)


def test_boolean_score_is_rejected() -> None:
    with pytest.raises(ValueError):
        VolatilityStateRequest(
            volatility_score=True,
            event_time=EVENT_TIME,
            received_at=EVENT_TIME,
            source_event_id="event-1",
        )


@pytest.mark.parametrize("field", ["event_time", "received_at"])
def test_non_utc_timestamps_fail(field: str) -> None:
    values: dict[str, object] = {
        "event_time": EVENT_TIME,
        "received_at": EVENT_TIME,
        "source_event_id": "event-1",
        "volatility_score": 0.0,
    }
    values[field] = datetime(2026, 1, 1)
    with pytest.raises(ValueError):
        VolatilityStateRequest(**values)  # type: ignore[arg-type]


def test_empty_source_event_id_fails() -> None:
    with pytest.raises(ValueError):
        VolatilityStateRequest(
            volatility_score=0.0,
            event_time=EVENT_TIME,
            received_at=EVENT_TIME,
            source_event_id="",
        )
