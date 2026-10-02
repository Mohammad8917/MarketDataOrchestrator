"""FILE: risk/pretrade_safety_gate.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Combine existing Decision, Cost, Liquidity, and Risk outputs into a deterministic final safety gate.
LAYER: risk
OWNS: Final pre-execution safety aggregation only.
DOES_NOT_OWN: signal generation, cost estimation, liquidity estimation, risk calculation, persistence, or execution.
DEPENDENCIES: hashlib, shared.contracts.cost, shared.contracts.liquidity, shared.contracts.pretrade_safety, risk.risk_engine, shared.models.decision
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from hashlib import sha256

from risk.risk_engine import RiskOutput
from shared.contracts.cost import CostOutput
from shared.contracts.liquidity import LiquidityOutput
from shared.contracts.pretrade_safety import PreTradeSafetyOutput
from shared.models.decision import DecisionOutput


class PreTradeSafetyGate:
    """Aggregate already-evaluated gates without recomputing any upstream metric."""

    contract_id = "pretrade_safety_boundary"
    contract_version = "1.0.0"

    def evaluate(
        self,
        decision: DecisionOutput,
        cost: CostOutput,
        liquidity: LiquidityOutput,
        risk: RiskOutput,
    ) -> PreTradeSafetyOutput:
        """Return NO_TRADE unless Decision, Cost, Liquidity, and Risk all permit action."""
        event_time = decision.event_time\n        for name, observation_time in (\n            ("cost", cost.event_time),\n            ("liquidity", liquidity.event_time),\n            ("risk", risk.event_time),\n        ):\n            if observation_time != event_time:\n                raise ValueError(f"{name} event_time must match decision event_time")\n\n        reasons: list[str] = []
        if decision.action == "WAIT":
            reasons.append("DECISION_WAIT")
        if not cost.approved:
            reasons.append("COST_REJECTED")
        if not liquidity.approved:
            reasons.append("LIQUIDITY_REJECTED")
        if not risk.approved:
            reasons.append("RISK_REJECTED")

        approved = not reasons and decision.action in {"BUY", "SELL"}
        action = decision.action if approved else "NO_TRADE"
        exposure = risk.exposure_fraction if approved else 0.0
        return PreTradeSafetyOutput(
            approved=approved,
            action=action,
            exposure_fraction=exposure,
            reasons=tuple(reasons),
            event_time=decision.event_time,
            safety_id=self._safety_id(decision, cost, liquidity, risk, approved),
        )

    @staticmethod
    def _safety_id(
        decision: DecisionOutput,
        cost: CostOutput,
        liquidity: LiquidityOutput,
        risk: RiskOutput,
        approved: bool,
    ) -> str:
        payload = (
            f"{decision.decision_id}|{cost.cost_id}|{liquidity.liquidity_id}|"
            f"{risk.risk_id}|{approved}"
        ).encode("utf-8")
        return sha256(payload).hexdigest()
