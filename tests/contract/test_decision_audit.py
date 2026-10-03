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


@pytest.mark.parametrize("value", ["", "   ", "\t\n"])
def test_audit_rejects_empty_contract_version(value: str) -> None:
    with pytest.raises(ValueError, match="contract_version must not be empty"):
        DecisionAuditRecord(
            decision_id="decision-1",
            cost_id="cost-1",
            liquidity_id="liquidity-1",
            risk_id="risk-1",
            safety_id="safety-1",
            action="BUY",
            reasons=(),
            event_time=_time(),
            audit_id="audit-1",
            contract_version=value,
        )


@pytest.mark.parametrize("reasons", [("",), ("   ",), ("valid", " ")])
def test_audit_rejects_empty_reason_values(reasons: tuple[str, ...]) -> None:
    with pytest.raises(ValueError, match="reasons must not contain empty values"):
        DecisionAuditRecord(
            decision_id="decision-1",
            cost_id="cost-1",
            liquidity_id="liquidity-1",
            risk_id="risk-1",
            safety_id="safety-1",
            action="NO_TRADE",
            reasons=reasons,
            event_time=_time(),
            audit_id="audit-1",
        )


@pytest.mark.parametrize("version", ["2.0.0", "0.9.0", "unknown"])
def test_audit_rejects_unsupported_contract_version(version: str) -> None:
    values = _base()
    values["contract_version"] = version
    with pytest.raises(ValueError, match="unsupported contract_version"):
        DecisionAuditRecord(**values)


def test_audit_rejects_non_string_reason_values() -> None:
    values = _base()
    values["reasons"] = ("valid", 1)
    with pytest.raises(ValueError, match="reasons must contain only strings"):
        DecisionAuditRecord(**values)


def test_audit_rejects_unsupported_action() -> None:
    values = _base()
    values["action"] = "WAIT"
    with pytest.raises(ValueError, match="unsupported action"):
        DecisionAuditRecord(**values)


def test_audit_rejects_market_context_time_mismatch() -> None:
    values = _base()
    values["market_context"] = __import__("shared.contracts.market_context", fromlist=["MarketContext"]).MarketContext(
        "Crypto",
        "BTCUSDT",
        "1h",
        datetime(2026, 10, 2, 0, 0, 1, tzinfo=timezone.utc),
        "evt-1",
    )
    with pytest.raises(ValueError, match="market context event_time"):
        DecisionAuditRecord(**values)


def test_audit_rejects_reasonless_no_trade() -> None:
    values = _base()
    values["reasons"] = ()
    with pytest.raises(ValueError, match="NO_TRADE audit record must contain reasons"):
        DecisionAuditRecord(**values)
