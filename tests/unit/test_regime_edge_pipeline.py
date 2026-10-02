"""Unit tests for regime-to-edge integration."""

from datetime import UTC, datetime

import pytest

from composition.confirmation_contract import ConfirmationOutput
from composition.regime_edge_pipeline import RegimeEdgeEvaluationPipeline
from regime.classification.regime_classifier import RegimeOutput
from regime.features.regime_features import RegimeFeatureSet
from regime.uncertainty.regime_uncertainty import RegimeUncertaintyOutput
from analysis.regime_analysis import RegimeAnalysisOutput
from shared.interfaces.setup import SetupOutput
from volatility.state.volatility_state import VolatilityStateOutput


NOW = datetime(2026, 10, 2, 13, tzinfo=UTC)


def _regime(label: str, confidence: float = 0.8) -> RegimeAnalysisOutput:
    return RegimeAnalysisOutput(
        features=RegimeFeatureSet(0.5, -0.25, NOW, "evt-1"),
        classification=RegimeOutput(label, confidence, NOW, "trend"),
        uncertainty=RegimeUncertaintyOutput(1.0 - confidence, NOW, "evt-1"),
        volatility_state=VolatilityStateOutput(-0.25, NOW, NOW, "evt-1"),
        event_time=NOW,
        received_at=NOW,
        source_event_id="evt-1",
    )


def _setup() -> SetupOutput:
    return SetupOutput("long", 0.8, NOW, "setup-1")


def _confirmation() -> ConfirmationOutput:
    return ConfirmationOutput(
        confirmed=True,
        score=0.75,
        event_time=NOW,
        confirmation_id="confirmation-1",
    )


def test_trend_regime_strength_is_bound_to_edge() -> None:
    output = RegimeEdgeEvaluationPipeline().evaluate(
        setup=_setup(),
        confirmation=_confirmation(),
        regime=_regime("trend_up", 0.8),
        liquidity_quality=0.9,
        cost_efficiency=0.6,
    )

    assert output.edge_score == pytest.approx((0.8 + 0.75 + 0.8 + 0.9 + 0.6) / 5)
    assert output.event_time == NOW


def test_non_directional_regime_maps_to_zero_alignment() -> None:
    output = RegimeEdgeEvaluationPipeline().evaluate(
        setup=_setup(),
        confirmation=_confirmation(),
        regime=_regime("range_high_volatility", 0.9),
        liquidity_quality=0.9,
        cost_efficiency=0.6,
    )

    assert output.edge_score == pytest.approx((0.8 + 0.75 + 0.0 + 0.9 + 0.6) / 5)


def test_regime_and_confirmation_must_share_event_time() -> None:
    confirmation = ConfirmationOutput(
        confirmed=True,
        score=0.75,
        event_time=datetime(2026, 10, 2, 14, tzinfo=UTC),
        confirmation_id="confirmation-1",
    )

    with pytest.raises(ValueError, match="regime event_time"):
        RegimeEdgeEvaluationPipeline().evaluate(
            setup=_setup(),
            confirmation=confirmation,
            regime=_regime("trend_up"),
            liquidity_quality=0.9,
            cost_efficiency=0.6,
        )
