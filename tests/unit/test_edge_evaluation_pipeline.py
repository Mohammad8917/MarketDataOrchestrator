"""FILE: tests/unit/test_edge_evaluation_pipeline.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify canonical confirmation-to-edge adaptation and point-in-time invariants.
LAYER: tests
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import UTC, datetime

import pytest

from composition.edge_evaluation_pipeline import EdgeEvaluationPipeline
from composition.confirmation_contract import ConfirmationOutput


NOW = datetime(2026, 10, 2, 9, tzinfo=UTC)


def confirmation(*, confirmed: bool = True, score: float = 0.75) -> ConfirmationOutput:
    return ConfirmationOutput(
        confirmed=confirmed,
        score=score,
        event_time=NOW,
        confirmation_id="confirmation-1",
    )


def test_pipeline_preserves_confirmation_provenance_and_strength() -> None:
    output = EdgeEvaluationPipeline().evaluate(
        setup_id="setup-1",
        setup_quality=0.8,
        confirmation=confirmation(score=-0.75),
        regime_alignment=0.7,
        liquidity_quality=0.9,
        cost_efficiency=0.6,
        event_time=NOW,
    )

    assert output.event_time == NOW
    assert output.edge_score == pytest.approx((0.8 + 0.75 + 0.7 + 0.9 + 0.6) / 5)


def test_pipeline_rejects_unconfirmed_input() -> None:
    with pytest.raises(ValueError, match="must be confirmed"):
        EdgeEvaluationPipeline().evaluate(
            setup_id="setup-1",
            setup_quality=0.8,
            confirmation=confirmation(confirmed=False),
            regime_alignment=0.7,
            liquidity_quality=0.9,
            cost_efficiency=0.6,
            event_time=NOW,
        )


def test_pipeline_rejects_event_time_mismatch() -> None:
    with pytest.raises(ValueError, match="event_time"):
        EdgeEvaluationPipeline().evaluate(
            setup_id="setup-1",
            setup_quality=0.8,
            confirmation=confirmation(),
            regime_alignment=0.7,
            liquidity_quality=0.9,
            cost_efficiency=0.6,
            event_time=datetime(2026, 10, 2, 10, tzinfo=UTC),
        )
