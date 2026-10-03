"""Contract tests for the decision audit boundary."""

from datetime import datetime, timezone
from typing import Any

import pytest

from shared.contracts.decision_audit import DecisionAuditRecord


def _time() -> datetime:
    return datetime(2026, 10, 2, tzinfo=timezone.utc)


def _base() -> dict[str, Any]:
    return {
        "decision_id": "decision-1",
        "cost_id": "cost-1",
        "liquidity_id": "liquidity-1",
        "risk_id": "risk-1",
        "safety_id": "safety-1",
        "action": "NO_TRADE",
        "reasons": ("COST_REJECTED",),
        "event_time": _time(),
        "audit_id": "audit-1",
    }


def test_audit_accepts_valid_record() -> None:
    assert DecisionAuditRecord(**_base()).audit_id == "audit-1"


@pytest.mark.parametrize("value", ["2026-10-02T00:00:00Z", None, 1])
def test_audit_rejects_invalid_event_time_runtime_types(value: object) -> None:
    values = _base()
    values["event_time"] = value
    with pytest.raises(ValueError, match="event_time must be a datetime"):
        DecisionAuditRecord(**values)


@pytest.mark.parametrize("value", [0, None, object()])
def test_audit_rejects_invalid_required_identity_runtime_types(value: object) -> None:
    values = _base()
    values["decision_id"] = value
    with pytest.raises(ValueError, match="decision_id must be a string"):
        DecisionAuditRecord(**values)


@pytest.mark.parametrize("value", [0, object()])
def test_audit_rejects_invalid_optional_identity_runtime_types(value: object) -> None:
    values = _base()
    values["edge_id"] = value
    with pytest.raises(ValueError, match="edge_id must be a string"):
        DecisionAuditRecord(**values)


@pytest.mark.parametrize("value", [0, None, object()])
def test_audit_rejects_invalid_action_runtime_types(value: object) -> None:
    values = _base()
    values["action"] = value
    with pytest.raises(ValueError, match="action must be a string"):
        DecisionAuditRecord(**values)


@pytest.mark.parametrize("value", [[], "COST_REJECTED", None])
def test_audit_rejects_invalid_reasons_runtime_types(value: object) -> None:
    values = _base()
    values["reasons"] = value
    with pytest.raises(ValueError, match="reasons must be a tuple"):
        DecisionAuditRecord(**values)


@pytest.mark.parametrize("value", [0, None, object()])
def test_audit_rejects_invalid_contract_version_runtime_types(value: object) -> None:
    values = _base()
    values["contract_version"] = value
    with pytest.raises(ValueError, match="contract_version must be a string"):
        DecisionAuditRecord(**values)


def test_audit_rejects_invalid_market_context_runtime_type() -> None:
    values = _base()
    values["market_context"] = object()
    with pytest.raises(ValueError, match="market_context must be a MarketContext"):
        DecisionAuditRecord(**values)
