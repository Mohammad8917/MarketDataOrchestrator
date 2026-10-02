"""FILE: tests/unit/test_liquidity_engine.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
RESPONSIBILITY: Verify deterministic liquidity sufficiency and participation invariants.
LAYER: tests
PYTHON: >=3.13
"""

from datetime import UTC, datetime

import pytest

from liquidity.liquidity_engine import DeterministicLiquidityEngine
from shared.contracts.liquidity import LiquidityRequest


def _request(
    available: float = 0.8,
    required: float = 0.6,
    requested: float = 0.1,
    maximum: float = 0.2,
) -> LiquidityRequest:
    now = datetime(2026, 10, 2, 13, tzinfo=UTC)
    return LiquidityRequest(
        available_depth_fraction=available,
        required_depth_fraction=required,
        requested_participation_fraction=requested,
        max_participation_fraction=maximum,
        event_time=now,
        received_at=now,
        source_event_id="evt-1",
    )


@pytest.mark.parametrize(
    ("available", "required", "requested", "maximum", "approved"),
    [
        (0.8, 0.6, 0.1, 0.2, True),
        (0.6, 0.6, 0.2, 0.2, True),
        (0.5, 0.6, 0.1, 0.2, False),
        (0.8, 0.6, 0.3, 0.2, False),
    ],
)
def test_liquidity_gate(
    available: float,
    required: float,
    requested: float,
    maximum: float,
    approved: bool,
) -> None:
    output = DeterministicLiquidityEngine().evaluate(
        _request(available, required, requested, maximum)
    )
    assert output.approved is approved


def test_liquidity_id_is_deterministic() -> None:
    engine = DeterministicLiquidityEngine()
    assert engine.evaluate(_request()).liquidity_id == engine.evaluate(_request()).liquidity_id


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("available_depth_fraction", -0.1),
        ("required_depth_fraction", 1.1),
        ("requested_participation_fraction", -0.1),
        ("max_participation_fraction", 1.1),
    ],
)
def test_invalid_liquidity_bounds_rejected(field: str, value: float) -> None:
    values = {
        "available_depth_fraction": 0.8,
        "required_depth_fraction": 0.6,
        "requested_participation_fraction": 0.1,
        "max_participation_fraction": 0.2,
    }
    values[field] = value
    with pytest.raises(ValueError):
        LiquidityRequest(
            available_depth_fraction=values["available_depth_fraction"],
            required_depth_fraction=values["required_depth_fraction"],
            requested_participation_fraction=values["requested_participation_fraction"],
            max_participation_fraction=values["max_participation_fraction"],
            event_time=datetime(2026, 10, 2, 13, tzinfo=UTC),
            received_at=datetime(2026, 10, 2, 13, tzinfo=UTC),
            source_event_id="evt-1",
        )
