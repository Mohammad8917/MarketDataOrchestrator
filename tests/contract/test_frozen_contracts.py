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
DEPENDENCIES: dataclasses, datetime, decimal, typing, composition.composer, domain.common.timeframe, domain.market_data_event, indicators.core.base, regime.classification.regime_classifier, regime.uncertainty.regime_uncertainty, risk.risk_engine, shared.contracts.performance_metrics, shared.interfaces.strategy, shared.models.decision, shared.models.evidence
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

from composition.composer import CompositionOutput, CompositionRequest
from domain.common.timeframe import Timeframe
from domain.market_data_event import MarketDataEvent
from indicators.core.base import IndicatorOutput, IndicatorRequest
from regime.classification.regime_classifier import RegimeOutput, RegimeRequest
from regime.uncertainty.regime_uncertainty import (
    RegimeUncertaintyOutput,
    RegimeUncertaintyRequest,
)
from risk.risk_engine import RiskOutput, RiskRequest
from shared.contracts.performance_metrics import PerformanceMetricsData
from shared.interfaces.strategy import StrategyOutput, StrategyRequest
from shared.models.decision import DecisionOutput, DecisionRequest
from shared.models.evidence import ProvenanceMetadata


FROZEN_CONTRACT_TYPES = (
    IndicatorRequest,
    IndicatorOutput,
    RegimeRequest,
    RegimeOutput,
    RegimeUncertaintyRequest,
    RegimeUncertaintyOutput,
    CompositionRequest,
    CompositionOutput,
    StrategyRequest,
    StrategyOutput,
    ProvenanceMetadata,
    DecisionRequest,
    DecisionOutput,
    RiskRequest,
    RiskOutput,
    MarketDataEvent,
    PerformanceMetricsData,
)


def assert_frozen(instance: Any, field: str, value: Any) -> None:
    """Verify runtime immutability by attempting an intentional mutation."""
    with pytest.raises(FrozenInstanceError):
        setattr(cast(Any, instance), field, value)


def _valid_instance(contract_type: type[Any]) -> Any:
    """Construct one valid instance for each canonical frozen contract type."""
    now = datetime(2026, 9, 24, 9, tzinfo=UTC)
    values: dict[str, Any] = {
        "series": {"close": (100.0,)},
        "features": {"x": (1.0,)},
        "signals": {"x": 1.0},
        "inputs": {"x": 1.0},
        "decision_inputs": {"x": 1.0},
        "values": {"x": 1.0},
    }
    if contract_type is IndicatorRequest:
        return contract_type(
            series=values["series"], event_time=now, received_at=now, source_event_id="evt-1"
        )
    if contract_type is IndicatorOutput:
        return contract_type(values["values"], now, "indicator")
    if contract_type is RegimeRequest:
        return contract_type(values["features"], now, now, "evt-1")
    if contract_type is RegimeOutput:
        return contract_type("neutral", 0.5, now, "regime")
    if contract_type is RegimeUncertaintyRequest:
        return contract_type(0.5, now, now, "evt-1")
    if contract_type is RegimeUncertaintyOutput:
        return contract_type(0.5, now, "evt-1")
    if contract_type is CompositionRequest:
        return contract_type(values["signals"], now, now, "evt-1")
    if contract_type is CompositionOutput:
        return contract_type(1.0, now, "composition")
    if contract_type is StrategyRequest:
        return contract_type(values["inputs"], now, now, "evt-1")
    if contract_type is StrategyOutput:
        return contract_type("hold", 0.5, now, "strategy")
    if contract_type is ProvenanceMetadata:
        return contract_type("evt-1", "provider", now, now, "sha256:abc")
    if contract_type is DecisionRequest:
        return contract_type(values["inputs"], now, now, "evt-1")
    if contract_type is DecisionOutput:
        return contract_type("hold", 0.5, now, "decision")
    if contract_type is RiskRequest:
        return contract_type(values["decision_inputs"], now, now, "evt-1")
    if contract_type is RiskOutput:
        return contract_type(True, 0.25, now, "risk")
    if contract_type is PerformanceMetricsData:
        return contract_type(
            observations=2,
            initial_equity=Decimal("100"),
            final_equity=Decimal("110"),
            total_return=Decimal("0.1"),
            max_drawdown=Decimal("0"),
        )
    if contract_type is MarketDataEvent:
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
    raise AssertionError(f"unregistered frozen contract type: {contract_type!r}")


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
