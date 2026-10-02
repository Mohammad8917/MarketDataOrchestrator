"""FILE: risk/decision_risk_gate.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Adapt canonical DecisionOutput into the deterministic Risk boundary.
LAYER: risk
OWNS: Explicit Decision-to-Risk mapping and point-in-time handoff only.
DOES_NOT_OWN: decision generation, cost/liquidity estimation, portfolio construction, persistence, or execution.
DEPENDENCIES: risk.risk_engine; shared.models.decision
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from datetime import datetime

from risk.risk_engine import DeterministicRiskEngine, RiskOutput, RiskRequest
from shared.models.decision import DecisionOutput

_ACTION_TO_SIGNAL = {"BUY": 1.0, "SELL": -1.0, "WAIT": 0.0}


class DecisionRiskGate:
    """Hand off DecisionOutput to Risk without changing decision semantics."""

    def __init__(self, risk_engine: DeterministicRiskEngine | None = None) -> None:
        self.risk_engine = risk_engine or DeterministicRiskEngine()

    def evaluate(
        self,
        decision: DecisionOutput,
        received_at: datetime,
        requested_exposure: float,
        max_exposure: float,
    ) -> RiskOutput:
        """Convert a canonical decision into a bounded RiskRequest and evaluate it."""
        try:
            signal = _ACTION_TO_SIGNAL[decision.action]
        except KeyError as exc:
            raise ValueError(f"unsupported decision action: {decision.action!r}") from exc

        request = RiskRequest(
            decision_inputs={
                "signal": signal,
                "confidence": decision.confidence,
                "requested_exposure": requested_exposure,
                "max_exposure": max_exposure,
            },
            event_time=decision.event_time,
            received_at=received_at,
            source_event_id=decision.decision_id,
        )
        return self.risk_engine.evaluate(request)
