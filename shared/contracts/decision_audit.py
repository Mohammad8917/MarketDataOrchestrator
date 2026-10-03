"""FILE: shared/contracts/decision_audit.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.2.0
DATE_GREGORIAN: 2026-10-03
DATE_PERSIAN: 1405-07-11
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Define immutable reconstruction metadata for a completed analytical decision chain.
LAYER: shared
OWNS: Typed audit identity, upstream boundary references, and optional opportunity market provenance.
DOES_NOT_OWN: persistence, audit storage, execution, signal generation, cost/liquidity/risk calculation, or profitability claims.
DEPENDENCIES: dataclasses, datetime, shared.contracts.market_context
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from dataclasses import dataclass
from datetime import datetime, timezone

from shared.contracts.market_context import MarketContext

DECISION_AUDIT_CONTRACT_ID = "decision_audit_boundary"
DECISION_AUDIT_CONTRACT_VERSION = "1.2.0"

_ALLOWED_ACTIONS = frozenset({"BUY", "SELL", "NO_TRADE"})


def _utc(value: object, name: str) -> None:
    if not isinstance(value, datetime):
        raise ValueError(f"{name} must be a datetime")
    if value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
        raise ValueError(f"{name} must be timezone-aware UTC")


def _nonempty(value: object, name: str) -> None:
    if not isinstance(value, str):
        raise ValueError(f"{name} must be a string")
    if not value.strip():
        raise ValueError(f"{name} must not be empty")


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
    market_context: MarketContext | None = None
    contract_version: str = DECISION_AUDIT_CONTRACT_VERSION

    def __post_init__(self) -> None:
        _utc(self.event_time, "event_time")
        for name in ("decision_id", "cost_id", "liquidity_id", "risk_id", "safety_id", "audit_id"):
            _nonempty(getattr(self, name), name)
        for name in ("edge_id", "ranking_id", "selection_id"):
            value = getattr(self, name)
            if value is not None:
                _nonempty(value, name)
        if self.market_context is not None and not isinstance(self.market_context, MarketContext):
            raise ValueError("market_context must be a MarketContext when provided")
        if not isinstance(self.action, str):
            raise ValueError("action must be a string")
        if not isinstance(self.reasons, tuple):
            raise ValueError("reasons must be a tuple")
        if not all(isinstance(reason, str) for reason in self.reasons):
            raise ValueError("reasons must contain only strings")
        if any(not reason.strip() for reason in self.reasons):
            raise ValueError("reasons must not contain empty values")
        if not isinstance(self.contract_version, str):
            raise ValueError("contract_version must be a string")
        if not self.contract_version.strip():
            raise ValueError("contract_version must not be empty")
        if self.action not in _ALLOWED_ACTIONS:
            raise ValueError(f"unsupported action: {self.action!r}")
        if self.market_context is not None and self.market_context.event_time != self.event_time:
            raise ValueError("market context event_time must match audit event_time")
        if self.action == "NO_TRADE" and not self.reasons:
            raise ValueError("NO_TRADE audit record must contain reasons")
