"""Verify deterministic threshold confirmation methodology."""

from datetime import datetime, timezone
from math import inf, nan

import pytest

from composition.confirmation.deterministic_threshold import (
    CONFIRMATION_METHODOLOGY_ID,
    CONFIRMATION_THRESHOLD,
    DeterministicThresholdConfirmation,
)
from composition.confirmation_contract import ConfirmationRequest


def _request(signals: dict[str, float]) -> ConfirmationRequest:
    timestamp = datetime(2026, 10, 2, 12, 0, tzinfo=timezone.utc)
    return ConfirmationRequest(
        signals=signals,
        event_time=timestamp,
        received_at=timestamp,
        source_event_id="evt-confirmation-1",
    )


@pytest.mark.parametrize(
    ("signals", "expected"),
    [
        ({"trend": 0.8, "momentum": 0.4}, True),
        ({"trend": -0.8, "momentum": -0.4}, True),
        ({"trend": 0.8, "momentum": -0.2}, False),
        ({"trend": 0.5}, True),
        ({"trend": -0.5}, True),
    ],
)
def test_confirms_at_absolute_threshold(signals: dict[str, float], expected: bool) -> None:
    output = DeterministicThresholdConfirmation().confirm(_request(signals))
    assert output.confirmed is expected
    assert output.score == pytest.approx(sum(signals.values()) / len(signals))
    assert output.confirmation_id == CONFIRMATION_METHODOLOGY_ID
    assert CONFIRMATION_THRESHOLD == 0.5


def test_is_invariant_to_signal_order() -> None:
    confirmer = DeterministicThresholdConfirmation()
    first = confirmer.confirm(_request({"a": 0.8, "b": -0.2, "c": 0.6}))
    second = confirmer.confirm(_request({"c": 0.6, "a": 0.8, "b": -0.2}))
    assert first == second


@pytest.mark.parametrize(
    "signals",
    [{}, {"trend": nan}, {"trend": inf}, {"trend": -inf}],
)
def test_rejects_empty_or_non_finite_signals(signals: dict[str, float]) -> None:
    with pytest.raises(ValueError):
        DeterministicThresholdConfirmation().confirm(_request(signals))


@pytest.mark.parametrize("value", [-1.000001, 1.000001])
def test_rejects_out_of_range_signal(value: float) -> None:
    with pytest.raises(ValueError, match=r"\[-1.0, 1.0\]"):
        DeterministicThresholdConfirmation().confirm(_request({"trend": value}))
