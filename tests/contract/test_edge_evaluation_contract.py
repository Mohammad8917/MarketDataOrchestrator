"""Contract tests for the immutable edge-evaluation boundary."""

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime

import pytest

from shared.contracts.edge_evaluation import (
    EdgeEvaluationOutput,
    EdgeEvaluationRequest,
)


NOW = datetime(2026, 10, 2, 12, 0, tzinfo=UTC)


def test_request_and_output_are_immutable() -> None:
    request = EdgeEvaluationRequest(0.8, 0.7, 0.6, 0.9, 0.5, NOW, "setup", "confirmation")
    output = EdgeEvaluationOutput(0.7, NOW, "edge")

    with pytest.raises(FrozenInstanceError):
        request.setup_quality = 0.0  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        output.edge_score = 0.0  # type: ignore[misc]


def test_request_requires_utc_and_non_empty_sources() -> None:
    with pytest.raises(ValueError):
        EdgeEvaluationRequest(
            0.8, 0.7, 0.6, 0.9, 0.5, datetime(2026, 10, 2, 12), "setup", "confirmation"
        )

    with pytest.raises(ValueError):
        EdgeEvaluationRequest(0.8, 0.7, 0.6, 0.9, 0.5, NOW, "", "confirmation")


def test_output_rejects_out_of_bounds_score() -> None:
    with pytest.raises(ValueError):
        EdgeEvaluationOutput(1.01, NOW, "edge")

    with pytest.raises(ValueError):
        EdgeEvaluationOutput(-0.01, NOW, "edge")
