"""Unit tests for application-level opportunity orchestration."""

from dataclasses import dataclass
from datetime import UTC, datetime

import pytest

from analysis.regime_analysis import RegimeAnalysisOutput
from app.application import OpportunityApplication
from app.application_contract import ApplicationRequest
from composition.confirmation_contract import ConfirmationOutput
from composition.opportunity_chain_pipeline import ComposedOpportunityChainPipeline
from regime.classification.regime_classifier import RegimeOutput
from regime.features.regime_features import RegimeFeatureSet
from regime.uncertainty.regime_uncertainty import RegimeUncertaintyOutput
from shared.contracts.cost import CostOutput
from shared.contracts.liquidity import LiquidityOutput
from shared.contracts.opportunity_selection import OpportunitySelectionOutput
from shared.contracts.pretrade_safety import PreTradeSafetyOutput
from shared.interfaces.setup import SetupOutput
from shared.models.decision import DecisionOutput
from volatility.state.volatility_state import VolatilityStateOutput


NOW = datetime(2026, 10, 2, 13, tzinfo=UTC)


@dataclass(frozen=True, slots=True)
class AnalyticalPayload:
    decision: DecisionOutput
    safety: PreTradeSafetyOutput
    setup: SetupOutput
    confirmation: ConfirmationOutput
    regime: RegimeAnalysisOutput
    cost: CostOutput
    liquidity: LiquidityOutput
    liquidity_quality: float
    cost_efficiency: float


def _analytical_payload() -> AnalyticalPayload:
    return AnalyticalPayload(
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
        cost=CostOutput(True, 0.2, NOW, "cost-1"),
        liquidity=LiquidityOutput(True, NOW, "liquidity-1"),
        liquidity_quality=0.9,
        cost_efficiency=0.6,
    )


def _evaluate_composed(
    payload: AnalyticalPayload, limit: int
) -> OpportunitySelectionOutput:
    return ComposedOpportunityChainPipeline().evaluate(
        decision=payload.decision,
        safety=payload.safety,
        setup=payload.setup,
        confirmation=payload.confirmation,
        regime=payload.regime,
        cost=payload.cost,
        liquidity=payload.liquidity,
        liquidity_quality=payload.liquidity_quality,
        cost_efficiency=payload.cost_efficiency,
        limit=limit,
    )


def _request(*, limit: int = 1) -> ApplicationRequest[AnalyticalPayload]:
    return ApplicationRequest(payload=_analytical_payload(), limit=limit)


def test_application_orchestrates_composed_chain() -> None:
    output = OpportunityApplication(_evaluate_composed).run(_request())

    assert len(output.selected) == 1
    assert output.selected[0].action == "BUY"
    assert output.selected[0].source_safety_id == "safety-1"
    assert output.selected[0].source_edge_id
    assert output.selection_id


@pytest.mark.parametrize("limit", [0, -1])
def test_application_request_rejects_invalid_limit(limit: int) -> None:
    with pytest.raises(ValueError, match="limit must be at least 1"):
        _request(limit=limit)


def test_application_propagates_upstream_cost_rejection() -> None:
    payload = _analytical_payload()
    rejected = AnalyticalPayload(
        decision=payload.decision,
        safety=payload.safety,
        setup=payload.setup,
        confirmation=payload.confirmation,
        regime=payload.regime,
        cost=CostOutput(False, 0.2, NOW, "cost-1"),
        liquidity=payload.liquidity,
        liquidity_quality=payload.liquidity_quality,
        cost_efficiency=payload.cost_efficiency,
    )
    request = ApplicationRequest(payload=rejected, limit=1)

    with pytest.raises(ValueError, match="cost must be approved"):
        OpportunityApplication(_evaluate_composed).run(request)


def test_application_request_is_immutable() -> None:
    request = _request()
    with pytest.raises(AttributeError):
        request.__setattr__("limit", 2)
