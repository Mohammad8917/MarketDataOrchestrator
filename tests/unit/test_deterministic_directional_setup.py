"""Verify the deterministic directional setup methodology."""

from datetime import datetime, timezone

import pytest

from analysis.setup.deterministic_directional_setup import (
    SETUP_DIRECTION_THRESHOLD,
    SETUP_METHODOLOGY_ID,
    SETUP_METHODOLOGY_VERSION,
    DeterministicDirectionalSetup,
)
from shared.interfaces.setup import SetupRequest


def _request(values: dict[str, float]) -> SetupRequest:
    now = datetime(2026, 10, 2, 10, 0, tzinfo=timezone.utc)
    return SetupRequest(values, now, now, "evt-1")


def test_methodology_identity_and_contract_shape() -> None:
    methodology = DeterministicDirectionalSetup()
    assert methodology.setup_id == SETUP_METHODOLOGY_ID
    assert SETUP_METHODOLOGY_VERSION == "1.0.0"
    assert methodology.contract_version == "1.0.0"


@pytest.mark.parametrize(
    ("values", "direction"),
    [
        ({"a": 1.0, "b": 0.5}, "bullish"),
        ({"a": -1.0, "b": -0.5}, "bearish"),
        ({"a": 0.4, "b": -0.4}, "neutral"),
    ],
)
def test_direction_is_deterministic(values: dict[str, float], direction: str) -> None:
    output = DeterministicDirectionalSetup().evaluate(_request(values))
    assert output.direction == direction


def test_threshold_is_inclusive() -> None:
    output = DeterministicDirectionalSetup().evaluate(
        _request({"a": SETUP_DIRECTION_THRESHOLD, "b": SETUP_DIRECTION_THRESHOLD})
    )
    assert output.direction == "bullish"
    assert output.strength == pytest.approx(SETUP_DIRECTION_THRESHOLD)


@pytest.mark.parametrize(
    ("values", "strength"),
    [
        ({"a": 0.2, "b": 0.6}, 0.4),
        ({"a": -0.2, "b": -0.6}, 0.4),
    ],
)
def test_strength_is_absolute_aggregate(values: dict[str, float], strength: float) -> None:
    output = DeterministicDirectionalSetup().evaluate(_request(values))
    assert output.strength == pytest.approx(strength)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf"), 1.01, -1.01])
def test_invalid_evidence_is_rejected(value: float) -> None:
    with pytest.raises(ValueError):
        DeterministicDirectionalSetup().evaluate(_request({"a": value}))
