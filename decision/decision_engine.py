"""FILE: decision/decision_engine.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Evaluate normalized actionable intent at the canonical decision boundary.
LAYER: decision
OWNS: Deterministic action classification from bounded analytical inputs.
DOES_NOT_OWN: risk sizing, provider I/O, persistence, execution, calibration, profitability claims.
DEPENDENCIES: shared.models.decision
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from hashlib import sha256

from shared.models.decision import DecisionOutput, DecisionRequest

DECISION_CONTRACT_ID = "decision_evaluation_boundary"
DECISION_CONTRACT_VERSION = "1.0.0"

_SIGNAL_KEY = "signal"
_CONFIDENCE_KEY = "confidence"
_THRESHOLD = 0.5


class DeterministicDecisionEngine:
    """Map bounded analytical intent to BUY/SELL/WAIT without owning risk."""

    contract_id = DECISION_CONTRACT_ID
    contract_version = DECISION_CONTRACT_VERSION

    def evaluate(self, request: DecisionRequest) -> DecisionOutput:
        """Evaluate one point-in-time request using fixed, market-agnostic rules."""
        signal = self._bounded_input(request, _SIGNAL_KEY)
        confidence = self._bounded_input(request, _CONFIDENCE_KEY)
        action = self._classify(signal, confidence)
        decision_id = self._decision_id(request, action, confidence)
        return DecisionOutput(
            action=action,
            confidence=confidence,
            event_time=request.event_time,
            decision_id=decision_id,
        )

    @staticmethod
    def _bounded_input(request: DecisionRequest, key: str) -> float:
        try:
            value = float(request.inputs[key])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"inputs must contain numeric {key!r}") from exc
        if key == _CONFIDENCE_KEY:
            valid = 0.0 <= value <= 1.0
        else:
            valid = -1.0 <= value <= 1.0
        if not valid:
            raise ValueError(f"{key} must be within its normalized bounds")
        return value

    @staticmethod
    def _classify(signal: float, confidence: float) -> str:
        if confidence < _THRESHOLD or abs(signal) < _THRESHOLD:
            return "WAIT"
        return "BUY" if signal > 0.0 else "SELL"

    @staticmethod
    def _decision_id(request: DecisionRequest, action: str, confidence: float) -> str:
        payload = (
            f"{request.source_event_id}|{request.event_time.isoformat()}|{action}|{confidence:.12f}"
        ).encode("utf-8")
        return sha256(payload).hexdigest()
