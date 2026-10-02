"""FILE: tests/unit/test_cost_engine.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
RESPONSIBILITY: Verify deterministic cost aggregation and hard acceptance invariants.
LAYER: tests
PYTHON: >=3.13
"""

from datetime import UTC, datetime

import pytest

from cost.cost_engine import DeterministicCostEngine
from shared.contracts.cost import CostRequest


def _request(
    spread: float = 0.001,
    slippage: float = 0.002,
    fee: float = 0.001,
    maximum: float = 0.005,
) -> CostRequest:
    now = datetime(2026, 10, 2, 12, tzinfo=UTC)
    return CostRequest(
        spread_fraction=spread,
        slippage_fraction=slippage,
        fee_fraction=fee,
        max_cost_fraction=maximum,
        event_time=now,
        received_at=now,
        source_event_id="evt-1",
    )


@pytest.mark.parametrize(
    ("spread", "slippage", "fee", "maximum", "approved", "total"),
    [
        (0.001, 0.002, 0.001, 0.005, True, 0.004),
        (0.002, 0.002, 0.001, 0.005, True, 0.005),
        (0.003, 0.002, 0.001, 0.005, False, 0.006),
        (0.0, 0.0, 0.0, 0.0, True, 0.0),
    ],
)
def test_cost_gate(
    spread: float,
    slippage: float,
    fee: float,
    maximum: float,
    approved: bool,
    total: float,
) -> None:
    output = DeterministicCostEngine().evaluate(
        _request(spread, slippage, fee, maximum)
    )
    assert output.approved is approved
    assert output.total_cost_fraction == pytest.approx(total)


def test_cost_id_is_deterministic() -> None:
    engine = DeterministicCostEngine()
    assert engine.evaluate(_request()).cost_id == engine.evaluate(_request()).cost_id


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("spread_fraction", -0.001),
        ("slippage_fraction", 1.001),
        ("fee_fraction", -0.001),
        ("max_cost_fraction", 1.001),
    ],
)
def test_invalid_cost_bounds_rejected(field: str, value: float) -> None:
    values = {
        "spread_fraction": 0.001,
        "slippage_fraction": 0.002,
        "fee_fraction": 0.001,
        "max_cost_fraction": 0.005,
    }
    values[field] = value
    with pytest.raises(ValueError):
        CostRequest(
            spread_fraction=values["spread_fraction"],
            slippage_fraction=values["slippage_fraction"],
            fee_fraction=values["fee_fraction"],
            max_cost_fraction=values["max_cost_fraction"],
            event_time=datetime(2026, 10, 2, 12, tzinfo=UTC),
            received_at=datetime(2026, 10, 2, 12, tzinfo=UTC),
            source_event_id="evt-1",
        )
