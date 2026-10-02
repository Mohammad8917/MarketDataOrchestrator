"""FILE: tests/unit/test_decision_risk_gate.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
RESPONSIBILITY: Verify explicit Decision-to-Risk handoff semantics.
LAYER: tests
PYTHON: >=3.13
"""

from datetime import UTC, datetime

import pytest

from risk.decision_risk_gate import DecisionRiskGate
from shared.models.decision import DecisionOutput


def _decision(action: str, confidence: float = 0.8) -> DecisionOutput:
    now = datetime(2026, 10, 2, 11, tzinfo=UTC)
    return DecisionOutput(
        action=action,
        confidence=confidence,
        event_time=now,
        decision_id="dec-1",
    )


@pytest.mark.parametrize(
    ("action", "approved"),
    [("BUY", True), ("SELL", True), ("WAIT", False)],
)
def test_decision_to_risk_mapping(action: str, approved: bool) -> None:
    output = DecisionRiskGate().evaluate(
        _decision(action),
        received_at=datetime(2026, 10, 2, 11, 1, tzinfo=UTC),
        requested_exposure=0.2,
        max_exposure=0.25,
    )
    assert output.approved is approved
    assert output.exposure_fraction == (0.2 if approved else 0.0)


def test_decision_event_time_and_id_are_preserved() -> None:
    decision = _decision("BUY")
    output = DecisionRiskGate().evaluate(
        decision,
        received_at=datetime(2026, 10, 2, 11, 1, tzinfo=UTC),
        requested_exposure=0.2,
        max_exposure=0.25,
    )
    assert output.event_time == decision.event_time
    assert output.risk_id


def test_risk_cap_is_enforced_after_decision() -> None:
    output = DecisionRiskGate().evaluate(
        _decision("BUY"),
        received_at=datetime(2026, 10, 2, 11, 1, tzinfo=UTC),
        requested_exposure=0.3,
        max_exposure=0.25,
    )
    assert output.approved is False
    assert output.exposure_fraction == 0.0


def test_unknown_decision_action_is_rejected() -> None:
    with pytest.raises(ValueError, match="unsupported decision action"):
        DecisionRiskGate().evaluate(
            _decision("NO_TRADE"),
            received_at=datetime(2026, 10, 2, 11, 1, tzinfo=UTC),
            requested_exposure=0.2,
            max_exposure=0.25,
        )
