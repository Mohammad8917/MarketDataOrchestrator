"""FILE: tests/contract/test_frozen_contracts.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.2.0
DATE_GREGORIAN: 2026-09-30
DATE_PERSIAN: 1405-07-08
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify declaration and runtime immutability of every canonical frozen contract data model.
LAYER: tests
OWNS: G03 frozen-contract declaration, mutation, and inventory guards.
DOES_NOT_OWN: Contract implementation behavior, security threat controls, or release approval.
DEPENDENCIES: dataclasses, datetime, decimal, typing, analysis.regime_analysis, composition.composer, domain.common.timeframe, domain.market_data_event, indicators.core.base, regime.classification.regime_classifier, regime.features.regime_features, regime.uncertainty.regime_uncertainty, risk.risk_engine, shared.contracts.market_structure, shared.contracts.performance_metrics, shared.interfaces.setup, shared.interfaces.strategy, shared.models.decision, shared.models.evidence, volatility.state.volatility_state
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from dataclasses import FrozenInstanceError, fields
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any, cast

import pytest

from analysis.regime_analysis import RegimeAnalysisOutput
from backtest.composition_replay import CompositionReplayOutput
from backtest.confirmation_replay import ConfirmationReplayOutput
from backtest.market_structure_replay import MarketStructureReplayOutput
from backtest.performance_replay import PerformanceAnalysisReplayOutput
from backtest.mtf_structure_replay import MtfStructureReplayOutput
from backtest.regime_analyzer import RegimeAnalysisReplayOutput
from backtest.setup_replay import SetupReplayOutput
from backtest.strategy_replay import StrategyReplayOutput
from composition.composer import CompositionOutput, CompositionRequest
from composition.confirmation_contract import ConfirmationOutput, ConfirmationRequest
from domain.common.timeframe import Timeframe
from domain.market_data_event import MarketDataEvent
from indicators.core.base import IndicatorOutput, IndicatorRequest
from regime.classification.regime_classifier import RegimeOutput, RegimeRequest
from regime.features.regime_features import RegimeFeatureSet
from regime.uncertainty.regime_uncertainty import (
    RegimeUncertaintyOutput,
    RegimeUncertaintyRequest,
)
from risk.risk_engine import RiskOutput, RiskRequest
from shared.contracts.market_structure import (
    MarketStructureBar,
    MarketStructureOutput,
    MarketStructureRequest,
    StructureEvent,
    StructurePoint,
    StructureState,
)
from shared.contracts.cost import CostOutput, CostRequest
from shared.contracts.liquidity import LiquidityOutput, LiquidityRequest
from shared.contracts.pretrade_safety import PreTradeSafetyOutput
from shared.contracts.decision_audit import DecisionAuditRecord
from shared.contracts.performance_metrics import PerformanceMetricsData
from shared.contracts.mtf_structure import (
    MtfStructureInput,
    MtfStructureObservation,
    MtfStructureOutput,
    MtfStructureRequest,
)
from shared.interfaces.setup import SetupOutput, SetupRequest
from shared.interfaces.strategy import StrategyOutput, StrategyRequest
from shared.models.decision import DecisionOutput, DecisionRequest
from shared.models.evidence import ProvenanceMetadata
from volatility.state.volatility_state import (
    VolatilityStateOutput,
    VolatilityStateRequest,
)


MARKET_STRUCTURE_CONTRACT_TYPES = (
    MarketStructureBar,
    MarketStructureRequest,
    StructurePoint,
    StructureEvent,
    StructureState,
    MarketStructureOutput,
)


FROZEN_CONTRACT_TYPES = (
    IndicatorRequest,
    IndicatorOutput,
    RegimeRequest,
    RegimeOutput,
    RegimeAnalysisOutput,
    RegimeAnalysisReplayOutput,
    CompositionReplayOutput,
    ConfirmationReplayOutput,
    MarketStructureReplayOutput,
    MtfStructureReplayOutput,
    SetupReplayOutput,
    StrategyReplayOutput,
    PerformanceAnalysisReplayOutput,
    RegimeUncertaintyRequest,
    RegimeUncertaintyOutput,
    VolatilityStateRequest,
    VolatilityStateOutput,
    CompositionRequest,
    CompositionOutput,
    ConfirmationRequest,
    ConfirmationOutput,
    SetupRequest,
    SetupOutput,
    StrategyRequest,
    StrategyOutput,
    ProvenanceMetadata,
    DecisionRequest,
    DecisionOutput,
    RiskRequest,
    RiskOutput,
    MarketDataEvent,
    PerformanceMetricsData,
    CostRequest,
    CostOutput,
    LiquidityRequest,
    LiquidityOutput,
    PreTradeSafetyOutput,
    MarketStructureBar,
    MarketStructureRequest,
    StructurePoint,
    StructureEvent,
    StructureState,
    MarketStructureOutput,
    MtfStructureInput,
    MtfStructureRequest,
    MtfStructureObservation,
    MtfStructureOutput,
)


def assert_frozen(instance: Any, field: str, value: Any) -> None:
    """Verify runtime immutability by attempting an intentional mutation."""
    with pytest.raises(FrozenInstanceError):
        setattr(cast(Any, instance), field, value)


def _base_contract_values() -> dict[str, Any]:
    return {
        "series": {"close": (100.0,)},
        "features": {"x": (1.0,)},
        "signals": {"x": 1.0},
        "inputs": {"x": 1.0},
        "decision_inputs": {"x": 1.0},
        "values": {"x": 1.0},
    }


def _simple_contract_instance(
    contract_type: type[Any], now: datetime, values: dict[str, Any]
) -> Any:
    constructors = {
        IndicatorRequest: lambda: contract_type(
            series=values["series"], event_time=now, received_at=now, source_event_id="evt-1"
        ),
        IndicatorOutput: lambda: contract_type(values["values"], now, "indicator"),
        RegimeRequest: lambda: contract_type(values["features"], now, now, "evt-1"),
        RegimeOutput: lambda: contract_type("neutral", 0.5, now, "regime"),
        RegimeUncertaintyRequest: lambda: contract_type(0.5, now, now, "evt-1"),
        RegimeUncertaintyOutput: lambda: contract_type(0.5, now, "evt-1"),
        VolatilityStateRequest: lambda: contract_type(0.5, now, now, "evt-1"),
        VolatilityStateOutput: lambda: contract_type(0.5, now, now, "evt-1"),
        CompositionRequest: lambda: contract_type(values["signals"], now, now, "evt-1"),
        CompositionOutput: lambda: contract_type(1.0, now, "composition"),
        ConfirmationRequest: lambda: contract_type(values["signals"], now, now, "evt-1"),
        ConfirmationOutput: lambda: contract_type(True, 1.0, now, "confirmation"),
        SetupRequest: lambda: contract_type(values["inputs"], now, now, "evt-1"),
        SetupOutput: lambda: contract_type("neutral", 0.5, now, "setup"),
        StrategyRequest: lambda: contract_type(values["inputs"], now, now, "evt-1"),
        StrategyOutput: lambda: contract_type("hold", 0.5, now, "strategy"),
        ProvenanceMetadata: lambda: contract_type("evt-1", "provider", now, now, "sha256:abc"),
        DecisionRequest: lambda: contract_type(values["inputs"], now, now, "evt-1"),
        DecisionOutput: lambda: contract_type("hold", 0.5, now, "decision"),
        RiskRequest: lambda: contract_type(values["decision_inputs"], now, now, "evt-1"),
        RiskOutput: lambda: contract_type(True, 0.25, now, "risk"),
        CostRequest: lambda: contract_type(0.001, 0.002, 0.001, 0.005, now, now, "evt-1"),
        CostOutput: lambda: contract_type(True, 0.004, now, "cost"),
        LiquidityRequest: lambda: contract_type(0.8, 0.6, 0.1, 0.2, now, now, "evt-1"),
        LiquidityOutput: lambda: contract_type(True, now, "liquidity"),
        PreTradeSafetyOutput: lambda: contract_type(True, "BUY", 0.2, (), now, "safety"),
        DecisionAuditRecord: lambda: contract_type(
            "d", "c", "l", "r", "s", "BUY", (), now, "audit"
        ),
        RegimeAnalysisReplayOutput: lambda: contract_type(()),
        CompositionReplayOutput: lambda: contract_type(()),
        ConfirmationReplayOutput: lambda: contract_type(()),
        MarketStructureReplayOutput: lambda: contract_type(()),
        MtfStructureReplayOutput: lambda: contract_type(()),
        SetupReplayOutput: lambda: contract_type(()),
        StrategyReplayOutput: lambda: contract_type(()),
        PerformanceAnalysisReplayOutput: lambda: contract_type(
            PerformanceMetricsData(2, Decimal("100"), Decimal("110"), Decimal("0.1"), Decimal("0"))
        ),
    }
    constructor = constructors.get(contract_type)
    return constructor() if constructor is not None else None


def _regime_analysis_instance(contract_type: type[Any], now: datetime) -> Any:
    features = RegimeFeatureSet(0.5, -0.25, now, "evt-1")
    classification = RegimeOutput("trend_up", 0.5, now, "trend")
    uncertainty = RegimeUncertaintyOutput(0.5, now, "evt-1")
    volatility = VolatilityStateOutput(-0.25, now, now, "evt-1")
    return contract_type(features, classification, uncertainty, volatility, now, now, "evt-1")


def _market_structure_instance(contract_type: type[Any], now: datetime) -> Any:
    bar = MarketStructureBar(
        event_time=now,
        received_at=now,
        source_event_id="evt-1",
        open=Decimal("100"),
        high=Decimal("110"),
        low=Decimal("90"),
        close=Decimal("105"),
        volume=Decimal("12.5"),
    )
    if contract_type is MarketStructureBar:
        return bar
    if contract_type is MarketStructureRequest:
        return contract_type((bar,), now, now, "evt-1")
    if contract_type is StructurePoint:
        return contract_type("HH", now, "evt-1", Decimal("110"))
    if contract_type is StructureEvent:
        return contract_type("breakout", now, "evt-1", Decimal("110"))
    if contract_type is StructureState:
        return contract_type("range", now, "evt-1")
    if contract_type is MtfStructureInput:
        structure = _market_structure_instance(MarketStructureOutput, now)
        return contract_type("higher", structure)
    if contract_type is MtfStructureObservation:
        return contract_type("higher", "bullish")
    if contract_type is MtfStructureRequest:
        structure = _market_structure_instance(MarketStructureOutput, now)
        return contract_type((MtfStructureInput("higher", structure),), now, now, "evt-1")
    if contract_type is MtfStructureOutput:
        return contract_type(
            (MtfStructureObservation("higher", "bullish"),),
            "bullish",
            now,
            "evt-1",
        )
    return contract_type((), (), None, now, "evt-1")


def _remaining_contract_instance(contract_type: type[Any], now: datetime) -> Any:
    if contract_type is PerformanceMetricsData:
        return contract_type(
            observations=2,
            initial_equity=Decimal("100"),
            final_equity=Decimal("110"),
            total_return=Decimal("0.1"),
            max_drawdown=Decimal("0"),
        )
    return contract_type.create(
        provider="provider",
        symbol="BTCUSDT",
        timeframe=Timeframe.parse("1m"),
        event_time=now,
        received_at=now,
        open=Decimal("100"),
        high=Decimal("110"),
        low=Decimal("90"),
        close=Decimal("105"),
        volume=Decimal("12.5"),
    )


def _valid_instance(contract_type: type[Any]) -> Any:
    now = datetime(2026, 9, 24, 9, tzinfo=UTC)
    values = _base_contract_values()
    if contract_type is RegimeAnalysisOutput:
        return _regime_analysis_instance(contract_type, now)
    if contract_type in MARKET_STRUCTURE_CONTRACT_TYPES:
        return _market_structure_instance(contract_type, now)
    if contract_type is MtfStructureInput:
        structure = _market_structure_instance(MarketStructureOutput, now)
        return MtfStructureInput("higher", structure)
    if contract_type is MtfStructureRequest:
        structure = _market_structure_instance(MarketStructureOutput, now)
        return MtfStructureRequest((MtfStructureInput("higher", structure),), now, now, "evt-1")
    if contract_type is MtfStructureObservation:
        return MtfStructureObservation("higher", "bullish")
    if contract_type is MtfStructureOutput:
        return MtfStructureOutput(
            (MtfStructureObservation("higher", "bullish"),),
            "bullish",
            now,
            "evt-1",
        )
    simple = _simple_contract_instance(contract_type, now, values)
    return simple if simple is not None else _remaining_contract_instance(contract_type, now)


@pytest.mark.parametrize("contract_type", FROZEN_CONTRACT_TYPES)
def test_every_canonical_frozen_contract_declares_frozen(contract_type: type[Any]) -> None:
    assert contract_type.__dataclass_params__.frozen is True


@pytest.mark.parametrize("contract_type", FROZEN_CONTRACT_TYPES)
def test_every_canonical_frozen_contract_rejects_runtime_mutation(
    contract_type: type[Any],
) -> None:
    instance = _valid_instance(contract_type)
    field_name = fields(contract_type)[0].name
    assert_frozen(instance, field_name, object())
