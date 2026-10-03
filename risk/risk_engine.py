"""FILE: risk/risk_engine.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.2.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Evaluate bounded decision intent against deterministic exposure and safety gates.
LAYER: risk
OWNS: Deterministic risk approval and bounded exposure calculation at the canonical risk boundary.
DOES_NOT_OWN: strategy selection, decision generation, provider I/O, persistence mutation, cost/liquidity estimation, or execution.
DEPENDENCIES: stdlib:dataclasses; stdlib:datetime; stdlib:hashlib; stdlib:typing
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from math import isfinite
from typing import Mapping

RISK_CONTRACT_ID = "risk_evaluation_boundary"
RISK_CONTRACT_VERSION = "1.0.0"

_SIGNAL_KEY = "signal"
_CONFIDENCE_KEY = "confidence"
_REQUESTED_EXPOSURE_KEY = "requested_exposure"
_MAX_EXPOSURE_KEY = "max_exposure"
_THRESHOLD = 0.5


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
class RiskRequest:
    decision_inputs: Mapping[str, float]
    event_time: datetime
    received_at: datetime
    source_event_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.decision_inputs, Mapping):
            raise ValueError("decision_inputs must be a mapping")
        _utc(self.event_time, "event_time")
        _utc(self.received_at, "received_at")
        if self.received_at < self.event_time:
            raise ValueError("received_at must not precede event_time")
        _nonempty(self.source_event_id, "source_event_id")


@dataclass(frozen=True, slots=True)
class RiskOutput:
    approved: bool
    exposure_fraction: float
    event_time: datetime
    risk_id: str
    contract_version: str = RISK_CONTRACT_VERSION

    def __post_init__(self) -> None:
        if type(self.approved) is not bool:
            raise ValueError("approved must be a bool")
        _utc(self.event_time, "event_time")
        _nonempty(self.risk_id, "risk_id")
        if isinstance(self.exposure_fraction, bool) or not isinstance(
            self.exposure_fraction, (int, float)
        ) or not isfinite(float(self.exposure_fraction)):
            raise ValueError("exposure_fraction must be a finite number")
        if not 0.0 <= self.exposure_fraction <= 1.0:
            raise ValueError("exposure_fraction must be between 0 and 1")
        if not isinstance(self.contract_version, str):
            raise ValueError("contract_version must be a string")
        if not self.contract_version.strip():
            raise ValueError("contract_version must not be empty")


class DeterministicRiskEngine:
    """Apply fixed, market-agnostic safety and exposure gates."""

    contract_id = RISK_CONTRACT_ID
    contract_version = RISK_CONTRACT_VERSION

    def evaluate(self, request: RiskRequest) -> RiskOutput:
        """Evaluate bounded decision intent without sizing beyond the supplied cap."""
        signal = self._bounded_input(request, _SIGNAL_KEY, -1.0, 1.0)
        confidence = self._bounded_input(request, _CONFIDENCE_KEY, 0.0, 1.0)
        requested = self._bounded_input(
            request,
            _REQUESTED_EXPOSURE_KEY,
            0.0,
            1.0,
        )
        maximum = self._bounded_input(request, _MAX_EXPOSURE_KEY, 0.0, 1.0)

        approved = abs(signal) >= _THRESHOLD and confidence >= _THRESHOLD and requested <= maximum
        exposure = requested if approved else 0.0
        return RiskOutput(
            approved=approved,
            exposure_fraction=exposure,
            event_time=request.event_time,
            risk_id=self._risk_id(request, approved, exposure),
        )

    @staticmethod
    def _bounded_input(
        request: RiskRequest,
        key: str,
        lower: float,
        upper: float,
    ) -> float:
        try:
            raw_value = request.decision_inputs[key]
        except (KeyError, TypeError) as exc:
            raise ValueError(f"decision_inputs must contain numeric {key!r}") from exc
        if isinstance(raw_value, bool) or not isinstance(raw_value, (int, float)):
            raise ValueError(f"decision_inputs must contain numeric {key!r}")
        value = float(raw_value)
        if not isfinite(value) or not lower <= value <= upper:
            raise ValueError(f"{key} must be between {lower} and {upper}")
        return value

    @staticmethod
    def _risk_id(request: RiskRequest, approved: bool, exposure: float) -> str:
        payload = (
            f"{request.source_event_id}|{request.event_time.isoformat()}|{approved}|{exposure:.12f}"
        ).encode("utf-8")
        return sha256(payload).hexdigest()
