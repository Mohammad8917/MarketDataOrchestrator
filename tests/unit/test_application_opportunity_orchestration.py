"""Unit tests for application-level opportunity orchestration."""

from datetime import UTC, datetime

import pytest

from composition.opportunity_chain_pipeline import ComposedOpportunityChainPipeline

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


def _analytical_payload() -> tuple[object, ...]:
    return (
        DecisionOutput("BUY", 0.9, NOW, "decision-1"),
        PreTradeSafetyOutput(True, "BUY", 0.2, (), NOW, "safety-1"),
        SetupOutput("bullish", 0.8, NOW, "setup-1"),
        ConfirmationOutput(True, 0.75, NOW, "confirmation-1"),
        RegimeAnalysisOutput(
            features=RegimeFeatureSet(0.5, -0.25, NOW, "evt-1"),
            classification=RegimeOutput("trend_up", 0.8, NOW, "regime-1"),
            uncertainty=RegimeUncertaintyOutput(0.2, NOW, "evt-1"),
            volatility_state=VolatilityStateOutput(-0.25, NOW, NOW, "evt-1"),
            event_time=NOW,
            received_at=NOW,
            source_event_id="evt-1",
        ),
        CostOutput(True, 0.2, NOW, "cost-1"),
        LiquidityOutput(True, NOW, "liquidity-1"),
        0.9,
        0.6,
    )


def _evaluate_composed(payload: tuple[object, ...], limit: int):
    (
        decision,
        safety,
        setup,
        confirmation,
        regime,
        cost,
        liquidity,
        liquidity_quality,
        cost_efficiency,
    ) = payload
    return ComposedOpportunityChainPipeline().evaluate(
        decision=decision,
        safety=safety,
        setup=setup,
        confirmation=confirmation,
        regime=regime,
        cost=cost,
        liquidity=liquidity,
        liquidity_quality=liquidity_quality,
        cost_efficiency=cost_efficiency,
        limit=limit,
    )


def _request(*, limit: int = 1) -> ApplicationRequest[tuple[object, ...]]:
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
    payload = list(_analytical_payload())
    payload[5] = CostOutput(False, 0.2, NOW, "cost-1")
    request = ApplicationRequest(payload=tuple(payload), limit=1)

    with pytest.raises(ValueError, match="cost must be approved"):
        OpportunityApplication(_evaluate_composed).run(request)


def test_application_request_is_immutable() -> None:
    request = _request()
    with pytest.raises(AttributeError):
        request.limit = 2
