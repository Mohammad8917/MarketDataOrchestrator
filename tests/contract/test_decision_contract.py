"""FILE: tests/contract/test_decision_contract.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify the canonical decision contract invariants.
LAYER: tests
OWNS: Decision contract verification.
DOES_NOT_OWN: production decision behavior.
DEPENDENCIES: stdlib:datetime; shared.models.decision
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timezone
import pytest
from shared.models.decision import DECISION_CONTRACT_ID, DecisionOutput, DecisionRequest


def test_decision_contract() -> None:
    now = datetime(2026, 9, 24, 8, tzinfo=timezone.utc)
    req = DecisionRequest({"signal": 1.0}, now, now, "evt-1")
    out = DecisionOutput("BUY", 0.8, now, "dec-1")
    assert DECISION_CONTRACT_ID == "decision_evaluation_boundary"
    assert req.source_event_id == "evt-1"
    assert out.confidence == 0.8
    with pytest.raises(AttributeError):
        out.action = "SELL"  # type: ignore[misc]


@pytest.mark.parametrize("value", [-0.1, 1.1])
def test_decision_confidence_bounds(value: float) -> None:
    now = datetime(2026, 9, 24, 8, tzinfo=timezone.utc)
    with pytest.raises(ValueError):
        DecisionOutput("BUY", value, now, "dec-1")


def test_decision_rejects_blank_source_event_id() -> None:
    now = datetime(2026, 9, 24, 8, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="source_event_id"):
        DecisionRequest({}, now, now, " ")


def test_decision_rejects_empty_contract_version() -> None:
    now = datetime(2026, 9, 24, 8, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="contract_version"):
        DecisionOutput("BUY", 0.5, now, "dec-1", "")


def test_decision_rejects_naive_time() -> None:
    now = datetime(2026, 9, 24, 8, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="UTC"):
        DecisionRequest({}, datetime(2026, 9, 24, 8), now, "evt-1")


def test_decision_rejects_received_at_before_event_time() -> None:
    event_time = datetime(2026, 9, 24, 8, tzinfo=timezone.utc)
    received_at = datetime(2026, 9, 24, 7, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="received_at must not precede event_time"):
        DecisionRequest({"signal": 1.0}, event_time, received_at, "evt-1")


@pytest.mark.parametrize("value", ["2026-01-01T00:00:00Z", 0, None])
def test_decision_rejects_invalid_timestamp_runtime_types(value: object) -> None:
    now = datetime(2026, 9, 24, 8, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="event_time must be a datetime"):
        DecisionRequest({}, value, now, "evt-1")  # type: ignore[arg-type]


@pytest.mark.parametrize("value", ["2026-01-01T00:00:00Z", 0, None])
def test_decision_rejects_invalid_received_at_runtime_types(value: object) -> None:
    now = datetime(2026, 9, 24, 8, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="received_at must be a datetime"):
        DecisionRequest({}, now, value, "evt-1")  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [0, None, object()])
def test_decision_rejects_invalid_source_event_id_runtime_types(value: object) -> None:
    now = datetime(2026, 9, 24, 8, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="source_event_id"):
        DecisionRequest({}, now, now, value)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [[], None, object()])
def test_decision_rejects_invalid_inputs_runtime_types(value: object) -> None:
    now = datetime(2026, 9, 24, 8, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="inputs must be a mapping"):
        DecisionRequest(value, now, now, "evt-1")  # type: ignore[arg-type]


@pytest.mark.parametrize("value", ["1.0", True, None, float("nan"), float("inf")])
def test_decision_rejects_invalid_input_value_runtime_types(value: object) -> None:
    now = datetime(2026, 9, 24, 8, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="inputs must contain only (numeric|finite) values"):
        DecisionRequest({"signal": value}, now, now, "evt-1")  # type: ignore[dict-item]


@pytest.mark.parametrize("value", ["BUY", 0, None])
def test_decision_output_rejects_invalid_action_runtime_types(value: object) -> None:
    if isinstance(value, str):
        pytest.skip("valid control")
    now = datetime(2026, 9, 24, 8, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="action must be a string"):
        DecisionOutput(value, 0.5, now, "dec-1")  # type: ignore[arg-type]


@pytest.mark.parametrize("value", ["dec-1", 0, None])
def test_decision_output_rejects_invalid_id_runtime_types(value: object) -> None:
    if isinstance(value, str):
        pytest.skip("valid control")
    now = datetime(2026, 9, 24, 8, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="decision_id must be a string"):
        DecisionOutput("BUY", 0.5, now, value)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", ["0.5", True, None, float("nan"), float("inf")])
def test_decision_output_rejects_invalid_confidence_runtime_types(value: object) -> None:
    now = datetime(2026, 9, 24, 8, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="confidence must be (numeric|finite and between)"):
        DecisionOutput("BUY", value, now, "dec-1")  # type: ignore[arg-type]
