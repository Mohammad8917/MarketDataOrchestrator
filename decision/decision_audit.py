"""FILE: decision/decision_audit.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Produce deterministic reconstruction metadata from completed decision-chain outputs.
LAYER: decision
OWNS: Audit identity construction and boundary-reference aggregation.
DOES_NOT_OWN: persistence, storage, signal generation, cost/liquidity/risk calculation, or execution.
DEPENDENCIES: hashlib, shared.contracts.decision_audit, shared.contracts.pretrade_safety
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from hashlib import sha256

from shared.contracts.decision_audit import DecisionAuditRecord
from shared.contracts.pretrade_safety import PreTradeSafetyOutput


class DecisionAuditRecorder:
    """Create immutable reconstruction metadata without persisting it."""

    contract_id = "decision_audit_boundary"
    contract_version = "1.0.0"

    def record(
        self,
        safety: PreTradeSafetyOutput,
        decision_id: str,
        cost_id: str,
        liquidity_id: str,
        risk_id: str,
    ) -> DecisionAuditRecord:
        """Aggregate canonical upstream IDs into a deterministic audit record."""
        payload = (
            f"{decision_id}|{cost_id}|{liquidity_id}|{risk_id}|"
            f"{safety.safety_id}|{safety.action}|{','.join(safety.reasons)}|"
            f"{safety.event_time.isoformat()}"
        ).encode("utf-8")
        return DecisionAuditRecord(
            decision_id=decision_id,
            cost_id=cost_id,
            liquidity_id=liquidity_id,
            risk_id=risk_id,
            safety_id=safety.safety_id,
            action=safety.action,
            reasons=safety.reasons,
            event_time=safety.event_time,
            audit_id=sha256(payload).hexdigest(),
        )
