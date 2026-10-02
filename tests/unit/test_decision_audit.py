"""FILE: tests/unit/test_decision_audit.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify deterministic decision-chain reconstruction metadata.
LAYER: tests
PYTHON: >=3.13
"""

from datetime import UTC, datetime

from decision.decision_audit import DecisionAuditRecorder
from shared.contracts.pretrade_safety import PreTradeSafetyOutput


def _safety() -> PreTradeSafetyOutput:
    return PreTradeSafetyOutput(
        approved=True,
        action="BUY",
        exposure_fraction=0.2,
        reasons=(),
        event_time=datetime(2026, 10, 2, 13, tzinfo=UTC),
        safety_id="safety-1",
    )


def test_audit_record_reconstructs_boundary_ids() -> None:
    record = DecisionAuditRecorder().record(
        _safety(),
        "decision-1",
        "cost-1",
        "liquidity-1",
        "risk-1",
    )
    assert record.decision_id == "decision-1"
    assert record.cost_id == "cost-1"
    assert record.liquidity_id == "liquidity-1"
    assert record.risk_id == "risk-1"
    assert record.safety_id == "safety-1"
    assert record.action == "BUY"


def test_audit_id_is_deterministic() -> None:
    recorder = DecisionAuditRecorder()
    first = recorder.record(_safety(), "d", "c", "l", "r")
    second = recorder.record(_safety(), "d", "c", "l", "r")
    assert first.audit_id == second.audit_id
