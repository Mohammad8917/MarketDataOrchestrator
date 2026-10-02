"""FILE: tests/unit/test_pretrade_safety_gate.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
RESPONSIBILITY: Verify deterministic final pre-trade safety aggregation.
LAYER: tests
PYTHON: >=3.13
"""

from datetime import UTC, datetime

import pytest

from risk.pretrade_safety_gate import PreTradeSafetyGate
from risk.risk_engine import RiskOutput
from shared.contracts.cost import CostOutput
from shared.contracts.liquidity import LiquidityOutput
from shared.models.decision import DecisionOutput


def _inputs() -> tuple[DecisionOutput, CostOutput, LiquidityOutput, RiskOutput]:
    now = datetime(2026, 10, 2, 13, tzinfo=UTC)
    return (
        DecisionOutput("BUY", 0.8, now, "dec-1"),
        CostOutput(True, 0.004, now, "cost-1"),
        LiquidityOutput(True, now, "liq-1"),
        RiskOutput(True, 0.2, now, "risk-1"),
    )


def test_all_gates_approve_buy() -> None:
    output = PreTradeSafetyGate().evaluate(*_inputs())
    assert output.approved is True
    assert output.action == "BUY"
    assert output.exposure_fraction == 0.2
    assert output.reasons == ("",)


@pytest.mark.parametrize(
    ("index", "replacement", "reason"),
    [
        (1, CostOutput(False, 0.01, datetime(2026, 10, 2, 13, tzinfo=UTC), "cost-2"), "COST_REJECTED"),
        (2, LiquidityOutput(False, datetime(2026, 10, 2, 13, tzinfo=UTC), "liq-2"), "LIQUIDITY_REJECTED"),
        (3, RiskOutput(False, 0.0, datetime(2026, 10, 2, 13, tzinfo=UTC), "risk-2"), "RISK_REJECTED"),
    ],
)
def test_rejected_gate_forces_no_trade(index: int, replacement: object, reason: str) -> None:
    values = list(_inputs())
    values[index] = replacement
    output = PreTradeSafetyGate().evaluate(*values)
    assert output.approved is False
    assert output.action == "NO_TRADE"
    assert reason in output.reasons
    assert output.exposure_fraction == 0.0


def test_wait_forces_no_trade() -> None:
    decision, cost, liquidity, risk = _inputs()
    decision = DecisionOutput("WAIT", 0.8, decision.event_time, decision.decision_id)
    output = PreTradeSafetyGate().evaluate(decision, cost, liquidity, risk)
    assert output.approved is False
    assert output.action == "NO_TRADE"
    assert output.reasons == ("DECISION_WAIT",)


def test_safety_id_is_deterministic() -> None:
    inputs = _inputs()
    engine = PreTradeSafetyGate()
    assert engine.evaluate(*inputs).safety_id == engine.evaluate(*inputs).safety_id
