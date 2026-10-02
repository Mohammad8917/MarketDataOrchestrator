"""Unit tests for the application opportunity orchestration boundary."""

from datetime import UTC, datetime

import pytest

from analysis.regime_analysis import RegimeAnalysisOutput
from app.application import OpportunityApplication
from app.application_contract import ApplicationRequest
from composition.confirmation_contract import ConfirmationOutput
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


def _request(*, cost_approved: bool = True) -> ApplicationRequest:
    return ApplicationRequest(
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


def test_application_delegates_to_canonical_opportunity_chain() -> None:
    output = OpportunityApplication().run(_request())

    assert len(output.selected) == 1
    assert output.selected[0].action == "BUY"
    assert output.selection_id


def test_application_propagates_upstream_cost_rejection() -> None:
    with pytest.raises(ValueError, match="cost must be approved"):
        OpportunityApplication().run(_request(cost_approved=False))


def test_application_contract_rejects_invalid_limit() -> None:
    request = _request()
    with pytest.raises(ValueError, match="limit must be at least 1"):
        ApplicationRequest(
            decision=request.decision,
            safety=request.safety,
            setup=request.setup,
            confirmation=request.confirmation,
            regime=request.regime,
            cost=request.cost,
            liquidity=request.liquidity,
            liquidity_quality=request.liquidity_quality,
            cost_efficiency=request.cost_efficiency,
            limit=0,
        )
