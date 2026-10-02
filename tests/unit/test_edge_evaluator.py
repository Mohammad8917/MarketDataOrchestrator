"""Focused unit tests for the deterministic edge-evaluation methodology."""

from datetime import UTC, datetime

import pytest

from analysis.edge_evaluator import DeterministicEdgeEvaluator
from shared.contracts.edge_evaluation import EdgeEvaluationRequest


NOW = datetime(2026, 10, 2, 12, 0, tzinfo=UTC)


def _request(**overrides: float | str | datetime) -> EdgeEvaluationRequest:
    values: dict[str, float | str | datetime] = {
        "setup_quality": 0.8,
        "confirmation_strength": 0.6,
        "regime_alignment": 0.7,
        "liquidity_quality": 0.9,
        "cost_efficiency": 0.5,
        "event_time": NOW,
        "source_setup_id": "setup-1",
        "source_confirmation_id": "confirmation-1",
    }
    values.update(overrides)
    return EdgeEvaluationRequest(**values)  # type: ignore[arg-type]


def test_equal_weight_edge_score_is_deterministic() -> None:
    output = DeterministicEdgeEvaluator().evaluate(_request())

    assert output.edge_score == pytest.approx(0.7)
    assert len(output.edge_id) == 64
    assert output.event_time == NOW


def test_same_input_produces_same_id_and_score() -> None:
    evaluator = DeterministicEdgeEvaluator()

    first = evaluator.evaluate(_request())
    second = evaluator.evaluate(_request())

    assert first == second


@pytest.mark.parametrize(
    "field",
    [
        "setup_quality",
        "confirmation_strength",
        "regime_alignment",
        "liquidity_quality",
        "cost_efficiency",
    ],
)
def test_component_bounds_are_enforced(field: str) -> None:
    with pytest.raises(ValueError):
        _request(**{field: 1.01})

    with pytest.raises(ValueError):
        _request(**{field: -0.01})
