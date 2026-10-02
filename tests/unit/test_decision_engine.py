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
