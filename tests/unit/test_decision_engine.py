"""FILE: tests/unit/test_decision_engine.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
RESPONSIBILITY: Verify deterministic decision methodology and invariants.
LAYER: tests
PYTHON: >=3.13
"""

from datetime import UTC, datetime

import pytest

from decision.decision_engine import DeterministicDecisionEngine
from shared.models.decision import DecisionRequest


def _request(signal: float, confidence: float) -> DecisionRequest:
    now = datetime(2026, 10, 2, 9, tzinfo=UTC)
    return DecisionRequest(
        inputs={"signal": signal, "confidence": confidence},
        event_time=now,
        received_at=now,
        source_event_id="evt-1",
    )


@pytest.mark.parametrize(
    ("signal", "confidence", "action"),
    [
        (0.8, 0.8, "BUY"),
        (-0.8, 0.8, "SELL"),
        (0.8, 0.4, "WAIT"),
        (0.4, 0.9, "WAIT"),
        (0.5, 0.5, "BUY"),
        (-0.5, 0.5, "SELL"),
    ],
)
def test_deterministic_decision(signal: float, confidence: float, action: str) -> None:
    output = DeterministicDecisionEngine().evaluate(_request(signal, confidence))
    assert output.action == action
    assert output.confidence == confidence


def test_decision_id_is_deterministic() -> None:
    engine = DeterministicDecisionEngine()
    assert (
        engine.evaluate(_request(0.8, 0.8)).decision_id
        == engine.evaluate(_request(0.8, 0.8)).decision_id
    )


@pytest.mark.parametrize("inputs", [{}, {"signal": 0.5}, {"confidence": 0.5}])
def test_missing_inputs_rejected(inputs: dict[str, float]) -> None:
    now = datetime(2026, 10, 2, 9, tzinfo=UTC)
    request = DecisionRequest(
        inputs=inputs,
        event_time=now,
        received_at=now,
        source_event_id="evt-1",
    )
    with pytest.raises(ValueError):
        DeterministicDecisionEngine().evaluate(request)


@pytest.mark.parametrize(
    ("signal", "confidence"),
    [(1.1, 0.5), (-1.1, 0.5), (0.5, 1.1), (0.5, -0.1)],
)
def test_out_of_bounds_rejected(signal: float, confidence: float) -> None:
    with pytest.raises(ValueError):
        DeterministicDecisionEngine().evaluate(_request(signal, confidence))


@pytest.mark.parametrize("value", ["0.8", True, None])
def test_bounded_input_rejects_coercible_non_numeric_values(value: object) -> None:
    class FakeRequest:
        inputs = {"signal": value}

    with pytest.raises(ValueError, match="inputs must contain"):
        DeterministicDecisionEngine._bounded_input(FakeRequest(), "signal")  # type: ignore[arg-type]


def test_engine_rejects_non_request_runtime_object() -> None:
    with pytest.raises(TypeError, match="request must be a DecisionRequest"):
        DeterministicDecisionEngine().evaluate(object())  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_bounded_input_rejects_non_finite_values(value: float) -> None:
    class FakeRequest:
        inputs = {"signal": value}

    with pytest.raises(ValueError, match="inputs must contain finite numeric"):
        DeterministicDecisionEngine._bounded_input(FakeRequest(), "signal")  # type: ignore[arg-type]


def test_zero_signal_is_wait_even_with_maximum_confidence() -> None:
    output = DeterministicDecisionEngine().evaluate(_request(0.0, 1.0))
    assert output.action == "WAIT"
    assert output.confidence == 1.0


def test_negative_boundary_signal_is_sell() -> None:
    output = DeterministicDecisionEngine().evaluate(_request(-1.0, 1.0))
    assert output.action == "SELL"
    assert output.confidence == 1.0


def test_decision_output_preserves_event_time_and_stable_identity() -> None:
    request = _request(0.75, 0.9)
    output = DeterministicDecisionEngine().evaluate(request)
    assert output.event_time == request.event_time
    assert output.decision_id == DeterministicDecisionEngine().evaluate(request).decision_id
    assert len(output.decision_id) == 64


def test_decision_id_changes_when_action_inputs_change() -> None:
    engine = DeterministicDecisionEngine()
    buy = engine.evaluate(_request(0.8, 0.8))
    sell = engine.evaluate(_request(-0.8, 0.8))
    wait = engine.evaluate(_request(0.8, 0.4))
    assert len({buy.decision_id, sell.decision_id, wait.decision_id}) == 3
