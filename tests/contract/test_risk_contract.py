"""FILE: tests/contract/test_risk_contract.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify the canonical risk contract invariants.
LAYER: tests
OWNS: Risk contract verification.
DOES_NOT_OWN: production risk behavior.
DEPENDENCIES: stdlib:datetime; risk.risk_engine
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timezone
import pytest
from risk.risk_engine import RISK_CONTRACT_ID, RiskOutput, RiskRequest


def test_risk_contract() -> None:
    now = datetime(2026, 9, 24, 8, tzinfo=timezone.utc)
    req = RiskRequest({"confidence": 0.8}, now, now, "evt-1")
    out = RiskOutput(True, 0.25, now, "risk-1")
    assert RISK_CONTRACT_ID == "risk_evaluation_boundary"
    assert req.source_event_id == "evt-1"
    assert out.approved is True
    with pytest.raises(AttributeError):
        out.approved = False  # type: ignore[misc]


@pytest.mark.parametrize("value", [-0.1, 1.1])
def test_risk_exposure_bounds(value: float) -> None:
    now = datetime(2026, 9, 24, 8, tzinfo=timezone.utc)
    with pytest.raises(ValueError):
        RiskOutput(True, value, now, "risk-1")


def test_risk_rejects_blank_source_event_id() -> None:
    now = datetime(2026, 9, 24, 8, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="source_event_id"):
        RiskRequest({}, now, now, " ")


def test_risk_rejects_empty_contract_version() -> None:
    now = datetime(2026, 9, 24, 8, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="contract_version"):
        RiskOutput(True, 0.5, now, "risk-1", "")


def test_risk_rejects_naive_time() -> None:
    now = datetime(2026, 9, 24, 8, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="UTC"):
        RiskRequest({}, datetime(2026, 9, 24, 8), now, "evt-1")


@pytest.mark.parametrize("value", [0, 1, 0.0, 1.0, "true", None])
def test_risk_output_rejects_non_boolean_approval(value: object) -> None:
    now = datetime(2026, 9, 24, 8, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="approved must be a bool"):
        RiskOutput(value, 0.25, now, "risk-1")  # type: ignore[arg-type]


@pytest.mark.parametrize("value", ["", "   ", "\t", "\n", None, 0])
def test_risk_output_rejects_invalid_contract_version(value: object) -> None:
    now = datetime(2026, 9, 24, 8, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="contract_version (must be a string|must not be empty)"):
        RiskOutput(True, 0.25, now, "risk-1", value)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [0, 1, 0.0, 1.0, "0.5", True, None])
def test_risk_engine_rejects_non_numeric_decision_inputs(value: object) -> None:
    now = datetime(2026, 9, 24, 8, tzinfo=timezone.utc)
    request = RiskRequest({"confidence": value}, now, now, "evt-1")  # type: ignore[dict-item]
    from risk.risk_engine import DeterministicRiskEngine

    with pytest.raises(ValueError, match="decision_inputs must contain numeric"):
        DeterministicRiskEngine()._bounded_input(request, "confidence", 0.0, 1.0)


def test_risk_request_rejects_non_mapping_inputs() -> None:
    now = datetime(2026, 9, 24, 8, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="decision_inputs must be a mapping"):
        RiskRequest(None, now, now, "evt-1")  # type: ignore[arg-type]


def test_risk_request_rejects_temporal_inversion() -> None:
    now = datetime(2026, 9, 24, 8, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="received_at must not precede event_time"):
        RiskRequest({}, now, datetime(2026, 9, 24, 7, tzinfo=timezone.utc), "evt-1")


@pytest.mark.parametrize("value", ["2026-01-01T00:00:00Z", 0, None])
def test_risk_request_rejects_invalid_datetime_runtime_type(value: object) -> None:
    now = datetime(2026, 9, 24, 8, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="event_time must be a datetime"):
        RiskRequest({}, value, now, "evt-1")  # type: ignore[arg-type]
