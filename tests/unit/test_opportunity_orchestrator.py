"""Unit tests for the opportunity orchestration composition root."""

from dataclasses import replace
from datetime import UTC, datetime
from typing import Any, cast

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
    assert output.market_context.market == "Crypto"
    assert output.market_context.symbol == "BTCUSDT"


@pytest.mark.parametrize("market", ["Crypto", "Forex", "Gold"])
def test_orchestrator_accepts_all_supported_markets(market: str) -> None:
    output = build_opportunity_orchestrator().run(_request(market=market))

    assert len(output.selected) == 1
    assert output.selected[0].action == "BUY"
    assert output.market_context.market == market


def test_orchestrator_rejects_market_context_source_event_mismatch() -> None:
    with pytest.raises(ValueError, match="market context source_event_id"):
        replace(
            _request(),
            market_context=replace(_request().market_context, source_event_id="evt-2"),
        )


def test_orchestrator_rejects_market_context_time_mismatch() -> None:
    with pytest.raises(ValueError, match="market context event_time"):
        replace(
            _request(),
            market_context=replace(
                _request().market_context,
                event_time=datetime(2026, 10, 2, 14, tzinfo=UTC),
            ),
        )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("market", []),
        ("symbol", object()),
        ("timeframe", object()),
        ("event_time", "2026-10-02T13:00:00Z"),
        ("source_event_id", []),
        ("contract_version", None),
    ],
)
def test_market_context_rejects_invalid_runtime_types(field: str, value: object) -> None:
    values: dict[str, object] = {
        "market": "Crypto",
        "symbol": "BTCUSDT",
        "timeframe": "1h",
        "event_time": NOW,
        "source_event_id": "evt-1",
        "contract_version": "1.0.0",
    }
    values[field] = value
    with pytest.raises(ValueError):
        MarketContext(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("market_context", None),
        ("decision", None),
        ("safety", None),
        ("setup", None),
        ("confirmation", None),
        ("regime", None),
        ("cost", None),
        ("liquidity", None),
    ],
)
def test_orchestration_input_rejects_invalid_upstream_runtime_types(
    field: str, value: object
) -> None:
    with pytest.raises(ValueError, match=field):
        replace(cast(Any, _request()), **{field: value})


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("liquidity_quality", True),
        ("liquidity_quality", "0.9"),
        ("liquidity_quality", float("nan")),
        ("liquidity_quality", float("inf")),
        ("cost_efficiency", False),
        ("cost_efficiency", "0.6"),
        ("cost_efficiency", float("nan")),
        ("cost_efficiency", float("-inf")),
    ],
)
def test_orchestration_input_rejects_nonfinite_or_wrong_numeric_types(
    field: str, value: object
) -> None:
    with pytest.raises(ValueError, match=field):
        replace(_request(), **{field: value})


@pytest.mark.parametrize("limit", [True, False, 1.0, "1", None])
def test_orchestration_input_rejects_non_integer_limits(limit: object) -> None:
    with pytest.raises(ValueError, match="limit"):
        replace(cast(Any, _request()), limit=limit)


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


def test_orchestrator_preserves_upstream_rejection() -> None:
    with pytest.raises(ValueError, match="cost must be approved"):
        build_opportunity_orchestrator().run(_request(cost_approved=False))
