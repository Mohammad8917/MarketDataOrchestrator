"""Unit tests for cost/liquidity-to-edge integration."""

from datetime import UTC, datetime

import pytest

from analysis.regime_analysis import RegimeAnalysisOutput
from composition.confirmation_contract import ConfirmationOutput
from composition.cost_liquidity_edge_pipeline import CostLiquidityEdgeEvaluationPipeline
from regime.classification.regime_classifier import RegimeOutput
from regime.features.regime_features import RegimeFeatureSet
from regime.uncertainty.regime_uncertainty import RegimeUncertaintyOutput
from shared.contracts.cost import CostOutput
from shared.contracts.liquidity import LiquidityOutput
from shared.interfaces.setup import SetupOutput
from volatility.state.volatility_state import VolatilityStateOutput


NOW = datetime(2026, 10, 2, 13, tzinfo=UTC)


def _setup() -> SetupOutput:
    return SetupOutput("bullish", 0.8, NOW, "setup-1")


def _confirmation() -> ConfirmationOutput:
    return ConfirmationOutput(True, 0.75, NOW, "confirmation-1")


def _regime() -> RegimeAnalysisOutput:
    return RegimeAnalysisOutput(
        features=RegimeFeatureSet(0.5, -0.25, NOW, "evt-1"),
        classification=RegimeOutput("trend_up", 0.8, NOW, "regime-1"),
        uncertainty=RegimeUncertaintyOutput(0.2, NOW, "evt-1"),
        volatility_state=VolatilityStateOutput(-0.25, NOW, NOW, "evt-1"),
        event_time=NOW,
        received_at=NOW,
        source_event_id="evt-1",
    )


def _cost(*, approved: bool = True, event_time: datetime = NOW) -> CostOutput:
    return CostOutput(approved, 0.2, event_time, "cost-1")


def _liquidity(*, approved: bool = True, event_time: datetime = NOW) -> LiquidityOutput:
    return LiquidityOutput(approved, event_time, "liquidity-1")


def test_pipeline_preserves_canonical_cost_liquidity_gates() -> None:
    output = CostLiquidityEdgeEvaluationPipeline().evaluate(
        setup=_setup(),
        confirmation=_confirmation(),
        regime=_regime(),
        cost=_cost(),
        liquidity=_liquidity(),
        liquidity_quality=0.9,
        cost_efficiency=0.6,
    )

    assert output.event_time == NOW
    assert output.edge_score == pytest.approx((0.8 + 0.75 + 0.8 + 0.9 + 0.6) / 5)


def test_pipeline_rejects_unapproved_cost() -> None:
    with pytest.raises(ValueError, match="cost must be approved"):
        CostLiquidityEdgeEvaluationPipeline().evaluate(
            setup=_setup(),
            confirmation=_confirmation(),
            regime=_regime(),
            cost=_cost(approved=False),
            liquidity=_liquidity(),
            liquidity_quality=0.9,
            cost_efficiency=0.6,
        )


def test_pipeline_rejects_unapproved_liquidity() -> None:
    with pytest.raises(ValueError, match="liquidity must be approved"):
        CostLiquidityEdgeEvaluationPipeline().evaluate(
            setup=_setup(),
            confirmation=_confirmation(),
            regime=_regime(),
            cost=_cost(),
            liquidity=_liquidity(approved=False),
            liquidity_quality=0.9,
            cost_efficiency=0.6,
        )


def test_pipeline_rejects_cost_event_time_mismatch() -> None:
    with pytest.raises(ValueError, match="cost event_time"):
        CostLiquidityEdgeEvaluationPipeline().evaluate(
            setup=_setup(),
            confirmation=_confirmation(),
            regime=_regime(),
            cost=_cost(event_time=datetime(2026, 10, 2, 14, tzinfo=UTC)),
            liquidity=_liquidity(),
            liquidity_quality=0.9,
            cost_efficiency=0.6,
        )


def test_pipeline_rejects_liquidity_event_time_mismatch() -> None:
    with pytest.raises(ValueError, match="liquidity event_time"):
        CostLiquidityEdgeEvaluationPipeline().evaluate(
            setup=_setup(),
            confirmation=_confirmation(),
            regime=_regime(),
            cost=_cost(),
            liquidity=_liquidity(event_time=datetime(2026, 10, 2, 14, tzinfo=UTC)),
            liquidity_quality=0.9,
            cost_efficiency=0.6,
        )
