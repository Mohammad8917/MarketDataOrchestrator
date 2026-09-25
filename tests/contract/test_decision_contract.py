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
