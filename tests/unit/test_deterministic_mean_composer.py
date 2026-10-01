"""FILE: tests/unit/test_deterministic_mean_composer.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-01
RESPONSIBILITY: Verify deterministic equal-weight signal composition methodology.
LAYER: tests
OWNS: Unit verification for deterministic_equal_weight_mean_v1.
DOES_NOT_OWN: strategy execution, decision finalization, risk
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timezone
from math import inf, nan

import pytest

from composition.composer import CompositionRequest
from composition.deterministic_mean import (
    COMPOSITION_METHODOLOGY_ID,
    DeterministicEqualWeightMeanComposer,
)


def _request(signals: dict[str, float]) -> CompositionRequest:
    now = datetime(2026, 10, 1, 12, 0, tzinfo=timezone.utc)
    return CompositionRequest(
        signals=signals,
        event_time=now,
        received_at=now,
        source_event_id="evt-composition-1",
    )


def test_composes_equal_weight_mean() -> None:
    output = DeterministicEqualWeightMeanComposer().compose(
        _request({"trend": 0.8, "momentum": 0.4, "structure": -0.2})
    )
    assert output.value == pytest.approx(1.0 / 3.0)
    assert output.composition_id == COMPOSITION_METHODOLOGY_ID


def test_is_invariant_to_signal_order() -> None:
    composer = DeterministicEqualWeightMeanComposer()
    first = composer.compose(_request({"a": 0.8, "b": -0.2, "c": 0.4}))
    second = composer.compose(_request({"c": 0.4, "a": 0.8, "b": -0.2}))
    assert first.value == second.value


@pytest.mark.parametrize("signals", [{}, {"trend": nan}, {"trend": inf}, {"trend": -inf}])
def test_rejects_empty_or_non_finite_signals(signals: dict[str, float]) -> None:
    with pytest.raises(ValueError):
        DeterministicEqualWeightMeanComposer().compose(_request(signals))


@pytest.mark.parametrize("value", [-1.000001, 1.000001])
def test_rejects_out_of_range_signal(value: float) -> None:
    with pytest.raises(ValueError, match=r"\[-1.0, 1.0\]"):
        DeterministicEqualWeightMeanComposer().compose(_request({"trend": value}))


@pytest.mark.parametrize("signals", [
    {"trend": -1.0},
    {"trend": 1.0},
    {"trend": 0.0, "momentum": 0.0},
])
def test_output_remains_bounded(signals: dict[str, float]) -> None:
    output = DeterministicEqualWeightMeanComposer().compose(_request(signals))
    assert -1.0 <= output.value <= 1.0
