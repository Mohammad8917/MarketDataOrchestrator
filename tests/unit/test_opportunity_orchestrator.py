"""Unit tests for the opportunity orchestration composition root."""

from dataclasses import replace
from datetime import UTC, datetime
from typing import cast

import pytest

from analysis.regime_analysis import RegimeAnalysisOutput
from composition.confirmation_contract import ConfirmationOutput
from orchestrator.opportunity_orchestrator import (
    OpportunityOrchestrationInput,
    build_opportunity_orchestrator,
)
from regime.classification.regime_classifier import RegimeOutput
from regime.features.regime_features import RegimeFeatureSet
from regime.uncertainty.regime_uncertainty import RegimeUncertaintyOutput
from shared.contracts.cost import CostOutput
from shared.contracts.liquidity import LiquidityOutput
from shared.contracts.market_context import Market, MarketContext
from shared.contracts.pretrade_safety import PreTradeSafetyOutput
from shared.interfaces.setup import SetupOutput
from shared.models.decision import DecisionOutput
from volatility.state.volatility_state import VolatilityStateOutput


NOW = datetime(2026, 10, 2, 13, tzinfo=UTC)


def _request(
    *, market: str = "Crypto", cost_approved: bool = True
) -> OpportunityOrchestrationInput:
    return OpportunityOrchestrationInput(
        market_context=MarketContext(
            cast(Market, market),
            "BTCUSDT" if market == "Crypto" else "EURUSD" if market == "Forex" else "XAUUSD",
            "1h",
            NOW,
            "evt-1",
        ),
        decision=DecisionOutput("BUY", 0.9, NOW, "decision-1"),
        safety=PreTradeSafetyOutput(True, "BUY", 0.2, (), NOW, "safety-1"),
        setup=SetupOutput("bullish", 0.8, NOW, "setup-1"),
        confirmation=ConfirmationOutput(True, 0.75, NOW, "confirmation-1"),
        regime=RegimeAnalysisOutput(
            features=RegimeFeatureSet(0.5, -0.25, NOW, "evt-1"),
            classification=RegimeOutput("trend_up", 0.8, NOW, "regime-1"),
            uncertainty=RegimeUncertaintyOutput(0.2, NOW, "evt-1"),
            volatility_state=VolatilityStateOutput(-0.25, NOW, NOW, "evt-1"),
            event_time=NOW,
            received_at=NOW,
            source_event_id="evt-1",
        ),
        cost=CostOutput(cost_approved, 0.2, NOW, "cost-1"),
        liquidity=LiquidityOutput(True, NOW, "liquidity-1"),
        liquidity_quality=0.9,
        cost_efficiency=0.6,
        limit=1,
    )


def test_orchestrator_builds_and_delegates_canonical_workflow() -> None:
    output = build_opportunity_orchestrator().run(_request())

    assert len(output.selected) == 1
    assert output.selected[0].action == "BUY"
    assert output.selected[0].source_safety_id == "safety-1"
    assert output.selected[0].source_edge_id
    assert output.selection_id


@pytest.mark.parametrize("market", ["Crypto", "Forex", "Gold"])
def test_orchestrator_accepts_all_supported_markets(market: str) -> None:
    output = build_opportunity_orchestrator().run(_request(market=market))

    assert len(output.selected) == 1
    assert output.selected[0].action == "BUY"


def test_orchestrator_preserves_upstream_rejection() -> None:
    with pytest.raises(ValueError, match="cost must be approved"):
        build_opportunity_orchestrator().run(_request(cost_approved=False))


@pytest.mark.parametrize(
    ("liquidity_quality", "cost_efficiency", "limit"),
    [(-0.01, 0.6, 1), (0.9, 1.01, 1), (0.9, 0.6, 0)],
)
def test_orchestration_input_rejects_invalid_lifecycle_values(
    liquidity_quality: float, cost_efficiency: float, limit: int
) -> None:
    with pytest.raises(ValueError):
        replace(
            _request(),
            liquidity_quality=liquidity_quality,
            cost_efficiency=cost_efficiency,
            limit=limit,
        )
