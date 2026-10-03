"""FILE: shared/contracts/pretrade_safety.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Define the immutable final analytical safety-gate result before execution.
LAYER: shared
OWNS: Typed pre-trade safety outcome and reason taxonomy.
DOES_NOT_OWN: execution, order submission, provider I/O, persistence mutation, portfolio construction, or profitability claims.
DEPENDENCIES: dataclasses, datetime, typing
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

import math
from dataclasses import dataclass
from datetime import datetime, timezone

PRETRADE_SAFETY_CONTRACT_ID = "pretrade_safety_boundary"
PRETRADE_SAFETY_CONTRACT_VERSION = "1.0.0"

_ALLOWED_ACTIONS = frozenset({"BUY", "SELL", "WAIT", "NO_TRADE"})
_ALLOWED_REASONS = frozenset(
    {"COST_REJECTED", "LIQUIDITY_REJECTED", "RISK_REJECTED", "DECISION_WAIT"}
)


def _utc(value: object, name: str) -> None:
    if not isinstance(value, datetime):
        raise ValueError(f"{name} must be a datetime")
    if value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
        raise ValueError(f"{name} must be timezone-aware UTC")


@dataclass(frozen=True, slots=True)
class PreTradeSafetyOutput:
    approved: bool
    action: str
    exposure_fraction: float
    reasons: tuple[str, ...]
    event_time: datetime
    safety_id: str
    contract_version: str = PRETRADE_SAFETY_CONTRACT_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.approved, bool):
            raise ValueError("approved must be a bool")
        if not isinstance(self.action, str):
            raise ValueError("action must be a string")
        if not isinstance(self.safety_id, str):
            raise ValueError("safety_id must be a string")
        if not isinstance(self.reasons, tuple):
            raise ValueError("reasons must be a tuple")
        if not isinstance(self.contract_version, str):
            raise ValueError("contract_version must be a string")
        if not self.contract_version.strip():
            raise ValueError("contract_version must not be empty")
        if self.contract_version != PRETRADE_SAFETY_CONTRACT_VERSION:
            raise ValueError("unsupported contract_version")
        _utc(self.event_time, "event_time")
        if self.action not in _ALLOWED_ACTIONS:
            raise ValueError(f"unsupported action: {self.action!r}")
        if isinstance(self.exposure_fraction, bool) or not isinstance(
            self.exposure_fraction, (int, float)
        ):
            raise ValueError("exposure_fraction must be numeric")
        if not math.isfinite(self.exposure_fraction) or not 0.0 <= self.exposure_fraction <= 1.0:
            raise ValueError("exposure_fraction must be finite and between 0 and 1")
        if not self.safety_id.strip():
            raise ValueError("safety_id must not be empty")
        if any(type(reason) is not str for reason in self.reasons):
            raise ValueError("reasons must contain only strings")
        if any(not reason.strip() for reason in self.reasons):
            raise ValueError("reasons must not contain blank values")
        if any(reason not in _ALLOWED_REASONS for reason in self.reasons):
            raise ValueError("reasons must contain only known safety reasons")
        if len(set(self.reasons)) != len(self.reasons):
            raise ValueError("reasons must not contain duplicates")
        if self.approved and self.action not in {"BUY", "SELL"}:
            raise ValueError("approved output must be BUY or SELL")
        if not self.approved and self.action != "NO_TRADE":
            raise ValueError("rejected output must be NO_TRADE")
        if self.approved and self.reasons:
            raise ValueError("approved output must not contain rejection reasons")
        if not self.approved and not self.reasons:
            raise ValueError("rejected output must contain a safety reason")
