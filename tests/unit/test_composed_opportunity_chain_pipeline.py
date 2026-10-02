"""Unit tests for the composed opportunity-chain boundary."""

from datetime import UTC, datetime

import pytest

from analysis.regime_analysis import RegimeAnalysisOutput
from composition.confirmation_contract import ConfirmationOutput
from composition.cost_liquidity_edge_pipeline import CostLiquidityEdgeEvaluationPipeline
from composition.opportunity_chain_pipeline import ComposedOpportunityChainPipeline
from regime.classification.regime_classifier import RegimeOutput
from regime.features.regime_features import RegimeFeatureSet
from regime.uncertainty.regime_uncertainty import RegimeUncertaintyOutput
from shared.contracts.cost import CostOutput
from shared.contracts.liquidity import LiquidityOutput
from shared.contracts.pretrade_safety import PreTradeSafetyOutput
from shared.interfaces.setup import SetupOutput
from shared.models.decision import DecisionOutput
from volatility.state.volatility_state import VolatilityStateOutput


NOW = datetime(2026, 10, 2, 13, tzinfo=UTC)


def _decision() -> DecisionOutput:
    return DecisionOutput("BUY", 0.9, NOW, "decision-1")


def _safety() -> PreTradeSafetyOutput:
    return PreTradeSafetyOutput(True, "BUY", 0.2, (), NOW, "safety-1")


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


def _cost(*, approved: bool = True) -> CostOutput:
    return CostOutput(approved, 0.2, NOW, "cost-1")


def _liquidity(*, approved: bool = True) -> LiquidityOutput:
    return LiquidityOutput(approved, NOW, "liquidity-1")


def test_composed_pipeline_reaches_selection_from_canonical_inputs() -> None:
    output = ComposedOpportunityChainPipeline().evaluate(
        decision=_decision(),
        safety=_safety(),
        setup=_setup(),
        confirmation=_confirmation(),
        regime=_regime(),
        cost=_cost(),
        liquidity=_liquidity(),
        liquidity_quality=0.9,
        cost_efficiency=0.6,
        limit=1,
    )

    assert len(output.selected) == 1
    assert output.selected[0].action == "BUY"
    assert output.selected[0].source_safety_id == "safety-1"
    assert output.selected[0].source_edge_id == output.selected[0].source_edge_id
    assert output.selection_id


def test_composed_pipeline_propagates_cost_rejection() -> None:
    with pytest.raises(ValueError, match="cost must be approved"):
        ComposedOpportunityChainPipeline().evaluate(
            decision=_decision(),
            safety=_safety(),
            setup=_setup(),
            confirmation=_confirmation(),
            regime=_regime(),
            cost=_cost(approved=False),
            liquidity=_liquidity(),
            liquidity_quality=0.9,
            cost_efficiency=0.6,
            limit=1,
        )


def test_composed_pipeline_propagates_liquidity_rejection() -> None:
    with pytest.raises(ValueError, match="liquidity must be approved"):
        ComposedOpportunityChainPipeline().evaluate(
            decision=_decision(),
            safety=_safety(),
            setup=_setup(),
            confirmation=_confirmation(),
            regime=_regime(),
            cost=_cost(),
            liquidity=_liquidity(approved=False),
            liquidity_quality=0.9,
            cost_efficiency=0.6,
            limit=1,
        )
