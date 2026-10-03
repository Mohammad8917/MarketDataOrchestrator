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


def test_empty_evidence_is_rejected() -> None:
    with pytest.raises(ValueError, match="^inputs must not be empty$"):
        DeterministicDirectionalSetup().evaluate(_request({}))


def test_lower_threshold_is_inclusive() -> None:
    output = DeterministicDirectionalSetup().evaluate(
        _request({"a": -SETUP_DIRECTION_THRESHOLD, "b": -SETUP_DIRECTION_THRESHOLD})
    )
    assert output.direction == "bearish"
    assert output.strength == pytest.approx(SETUP_DIRECTION_THRESHOLD)


def test_single_evidence_value_preserves_direction_and_strength() -> None:
    output = DeterministicDirectionalSetup().evaluate(_request({"a": -0.75}))
    assert output.direction == "bearish"
    assert output.strength == pytest.approx(0.75)


def test_boundary_evidence_values_are_accepted() -> None:
    bullish = DeterministicDirectionalSetup().evaluate(_request({"a": 1.0}))
    bearish = DeterministicDirectionalSetup().evaluate(_request({"a": -1.0}))
    assert bullish.direction == "bullish"
    assert bullish.strength == 1.0
    assert bearish.direction == "bearish"
    assert bearish.strength == 1.0


def test_evidence_key_order_does_not_change_result() -> None:
    methodology = DeterministicDirectionalSetup()
    first = methodology.evaluate(_request({"a": 0.8, "b": -0.2, "c": 0.4}))
    second = methodology.evaluate(_request({"c": 0.4, "a": 0.8, "b": -0.2}))
    assert second.direction == first.direction
    assert second.strength == first.strength


def test_output_preserves_point_in_time_provenance() -> None:
    request = _request({"a": 0.7, "b": 0.3})
    output = DeterministicDirectionalSetup().evaluate(request)
    assert output.event_time == request.event_time
    assert output.setup_id == SETUP_METHODOLOGY_ID
