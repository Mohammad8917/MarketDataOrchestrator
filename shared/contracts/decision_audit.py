"""FILE: shared/contracts/decision_audit.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Define immutable reconstruction metadata for a completed analytical decision chain.
LAYER: shared
OWNS: Typed audit identity and upstream boundary references.
DOES_NOT_OWN: persistence, audit storage, execution, signal generation, cost/liquidity/risk calculation, or profitability claims.
DEPENDENCIES: dataclasses, datetime
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from dataclasses import dataclass
from datetime import datetime, timezone

DECISION_AUDIT_CONTRACT_ID = "decision_audit_boundary"
DECISION_AUDIT_CONTRACT_VERSION = "1.1.0"

_ALLOWED_ACTIONS = frozenset({"BUY", "SELL", "NO_TRADE"})


@dataclass(frozen=True, slots=True)
class DecisionAuditRecord:
    decision_id: str
    cost_id: str
    liquidity_id: str
    risk_id: str
    safety_id: str
    action: str
    reasons: tuple[str, ...]
    event_time: datetime
    audit_id: str
    edge_id: str | None = None
    ranking_id: str | None = None
    selection_id: str | None = None
    contract_version: str = DECISION_AUDIT_CONTRACT_VERSION

    def __post_init__(self) -> None:
        if self.event_time.tzinfo is None or self.event_time.utcoffset() != timezone.utc.utcoffset(
            self.event_time
        ):
            raise ValueError("event_time must be timezone-aware UTC")
        for name in ("decision_id", "cost_id", "liquidity_id", "risk_id", "safety_id", "audit_id"):
            if not getattr(self, name).strip():
                raise ValueError(f"{name} must not be empty")
        for name in ("edge_id", "ranking_id", "selection_id"):
            value = getattr(self, name)
            if value is not None and not value.strip():
                raise ValueError(f"{name} must not be empty when provided")
        if self.action not in _ALLOWED_ACTIONS:
            raise ValueError(f"unsupported action: {self.action!r}")
        if self.action == "NO_TRADE" and not self.reasons:
            raise ValueError("NO_TRADE audit record must contain reasons")
