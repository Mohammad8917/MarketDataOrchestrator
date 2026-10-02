"""FILE: tests/unit/test_risk_engine.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
RESPONSIBILITY: Verify deterministic risk methodology and safety invariants.
LAYER: tests
PYTHON: >=3.13
"""

from datetime import UTC, datetime

import pytest

from risk.risk_engine import DeterministicRiskEngine, RiskRequest


def _request(
    signal: float = 0.8,
    confidence: float = 0.8,
    requested_exposure: float = 0.2,
    max_exposure: float = 0.25,
) -> RiskRequest:
    now = datetime(2026, 10, 2, 10, tzinfo=UTC)
    return RiskRequest(
        decision_inputs={
            "signal": signal,
            "confidence": confidence,
            "requested_exposure": requested_exposure,
            "max_exposure": max_exposure,
        },
        event_time=now,
        received_at=now,
        source_event_id="evt-1",
    )


@pytest.mark.parametrize(
    ("signal", "confidence", "requested", "maximum", "approved", "exposure"),
    [
        (0.8, 0.8, 0.2, 0.25, True, 0.2),
        (-0.8, 0.8, 0.2, 0.25, True, 0.2),
        (0.5, 0.5, 0.25, 0.25, True, 0.25),
        (0.4, 0.9, 0.2, 0.25, False, 0.0),
        (0.8, 0.4, 0.2, 0.25, False, 0.0),
        (0.8, 0.8, 0.3, 0.25, False, 0.0),
    ],
)
def test_deterministic_risk_gate(
    signal: float,
    confidence: float,
    requested: float,
    maximum: float,
    approved: bool,
    exposure: float,
) -> None:
    output = DeterministicRiskEngine().evaluate(
        _request(signal, confidence, requested, maximum)
    )
    assert output.approved is approved
    assert output.exposure_fraction == exposure


def test_risk_id_is_deterministic() -> None:
    engine = DeterministicRiskEngine()
    assert engine.evaluate(_request()).risk_id == engine.evaluate(_request()).risk_id


@pytest.mark.parametrize(
    "key",
    ["signal", "confidence", "requested_exposure", "max_exposure"],
)
def test_missing_risk_input_rejected(key: str) -> None:
    request = _request()
    inputs = dict(request.decision_inputs)
    del inputs[key]
    invalid = RiskRequest(
        decision_inputs=inputs,
        event_time=request.event_time,
        received_at=request.received_at,
        source_event_id=request.source_event_id,
    )
    with pytest.raises(ValueError):
        DeterministicRiskEngine().evaluate(invalid)


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("signal", 1.1),
        ("signal", -1.1),
        ("confidence", 1.1),
        ("confidence", -0.1),
        ("requested_exposure", 1.1),
        ("requested_exposure", -0.1),
        ("max_exposure", 1.1),
        ("max_exposure", -0.1),
    ],
)
def test_risk_bounds_rejected(key: str, value: float) -> None:
    request = _request()
    inputs = dict(request.decision_inputs)
    inputs[key] = value
    invalid = RiskRequest(
        decision_inputs=inputs,
        event_time=request.event_time,
        received_at=request.received_at,
        source_event_id=request.source_event_id,
    )
    with pytest.raises(ValueError):
        DeterministicRiskEngine().evaluate(invalid)
