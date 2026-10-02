"""Unit tests for the composed opportunity-chain boundary."""

from datetime import UTC, datetime

import pytest

from analysis.regime_analysis import RegimeAnalysisOutput
from composition.confirmation_contract import ConfirmationOutput
from composition.opportunity_chain_pipeline import ComposedOpportunityChainPipeline
from regime.classification.regime_classifier import RegimeOutput
from regime.features.regime_features import RegimeFeatureSet
from regime.uncertainty.regime_uncertainty import RegimeUncertaintyOutput
from shared.contracts.cost import CostOutput
from shared.contracts.liquidity import LiquidityOutput
from shared.contracts.market_context import MarketContext
from shared.contracts.pretrade_safety import PreTradeSafetyOutput
from shared.interfaces.setup import SetupOutput
from shared.models.decision import DecisionOutput
from volatility.state.volatility_state import VolatilityStateOutput


NOW = datetime(2026, 10, 2, 13, tzinfo=UTC)
CONTEXT = MarketContext("Crypto", "BTCUSDT", "1h", NOW, "evt-1")


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


def _evaluate(*, context: MarketContext = CONTEXT):
    return ComposedOpportunityChainPipeline().evaluate(
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
        market_context=context,
    )


def test_composed_pipeline_reaches_selection_from_canonical_inputs() -> None:
    output = _evaluate()

    assert len(output.selected) == 1
    assert output.selected[0].action == "BUY"
    assert output.selected[0].source_safety_id == "safety-1"
    assert output.selected[0].source_edge_id
    assert 0.0 <= output.selected[0].rank_score <= 1.0
    assert output.selection_id
    assert output.market_context == CONTEXT


def test_composed_pipeline_rejects_market_context_source_event_mismatch() -> None:
    mismatched = MarketContext("Crypto", "BTCUSDT", "1h", NOW, "evt-2")

    with pytest.raises(ValueError, match="market context source_event_id"):
        _evaluate(context=mismatched)


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
            market_context=CONTEXT,
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
            market_context=CONTEXT,
        )


@pytest.mark.parametrize(
    ("field", "expected_error"),
    [
        ("decision", "decision event_time"),
        ("safety", "safety event_time"),
        ("setup", "setup event_time"),
        ("confirmation", "confirmation event_time"),
        ("regime", "regime event_time"),
        ("cost", "cost event_time"),
        ("liquidity", "liquidity event_time"),
    ],
)
def test_composed_pipeline_rejects_temporal_misalignment(
    field: str,
    expected_error: str,
) -> None:
    mismatched_time = NOW.replace(minute=14)
    kwargs = {
        "decision": _decision(),
        "safety": _safety(),
        "setup": _setup(),
        "confirmation": _confirmation(),
        "regime": _regime(),
        "cost": _cost(),
        "liquidity": _liquidity(),
        "liquidity_quality": 0.9,
        "cost_efficiency": 0.6,
        "limit": 1,
        "market_context": CONTEXT,
    }

    value = kwargs[field]
    if field == "decision":
        kwargs[field] = DecisionOutput("BUY", 0.9, mismatched_time, "decision-1")
    elif field == "safety":
        kwargs[field] = PreTradeSafetyOutput(True, "BUY", 0.2, (), mismatched_time, "safety-1")
    elif field == "setup":
        kwargs[field] = SetupOutput("bullish", 0.8, mismatched_time, "setup-1")
    elif field == "confirmation":
        kwargs[field] = ConfirmationOutput(True, 0.75, mismatched_time, "confirmation-1")
    elif field == "regime":
        kwargs[field] = RegimeAnalysisOutput(
            features=RegimeFeatureSet(0.5, -0.25, mismatched_time, "evt-1"),
            classification=RegimeOutput("trend_up", 0.8, mismatched_time, "regime-1"),
            uncertainty=RegimeUncertaintyOutput(0.2, mismatched_time, "evt-1"),
            volatility_state=VolatilityStateOutput(
                -0.25,
                mismatched_time,
                mismatched_time,
                "evt-1",
            ),
            event_time=mismatched_time,
            received_at=mismatched_time,
            source_event_id="evt-1",
        )
    elif field == "cost":
        kwargs[field] = CostOutput(True, 0.2, mismatched_time, "cost-1")
    else:
        kwargs[field] = LiquidityOutput(True, mismatched_time, "liquidity-1")

    assert value.event_time == NOW
    with pytest.raises(ValueError, match=expected_error):
        ComposedOpportunityChainPipeline().evaluate(**kwargs)
