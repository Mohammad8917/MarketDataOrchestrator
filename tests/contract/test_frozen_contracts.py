"""FILE: tests/contract/test_frozen_contracts.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify declaration and runtime immutability of every canonical frozen contract data model.
LAYER: tests
OWNS: Reverse/static guards for canonical frozen contract models.
DOES_NOT_OWN: Mapping payload immutability, hostile object.__setattr__ resistance, provider transport.
DEPENDENCIES: stdlib:dataclasses; stdlib:typing; pytest; composition.composer; indicators.core.base; ingestion.interfaces.market_provider; regime.classification.regime_classifier; risk.risk_engine; shared.interfaces.strategy; shared.models.decision; shared.models.evidence
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from dataclasses import FrozenInstanceError, fields
from typing import Any, cast

import pytest

from composition.composer import CompositionOutput, CompositionRequest
from indicators.core.base import IndicatorOutput, IndicatorRequest
from ingestion.interfaces.market_provider import MarketEvent
from regime.classification.regime_classifier import RegimeOutput, RegimeRequest
from risk.risk_engine import RiskOutput, RiskRequest
from shared.interfaces.strategy import StrategyOutput, StrategyRequest
from shared.models.decision import DecisionOutput, DecisionRequest
from shared.models.evidence import ProvenanceMetadata


FROZEN_CONTRACT_TYPES = (
    IndicatorRequest,
    IndicatorOutput,
    RegimeRequest,
    RegimeOutput,
    CompositionRequest,
    CompositionOutput,
    StrategyRequest,
    StrategyOutput,
    ProvenanceMetadata,
    DecisionRequest,
    DecisionOutput,
    RiskRequest,
    RiskOutput,
    MarketEvent,
)


def assert_frozen(instance: Any, field: str, value: Any) -> None:
    """Verify runtime immutability by attempting an intentional mutation.

    Uses cast(Any) intentionally to bypass static typing because mypy cannot
    distinguish an intentional invalid assignment from an accidental one.
    """
    with pytest.raises(FrozenInstanceError):
        setattr(cast(Any, instance), field, value)


def _valid_instance(contract_type: type[Any]) -> Any:
    """Construct one valid instance for each canonical frozen contract type."""
    from datetime import UTC, datetime

    now = datetime(2026, 9, 24, 9, tzinfo=UTC)
    values: dict[str, Any] = {
        "series": {"close": (100.0,)},
        "features": {"x": (1.0,)},
        "signals": {"x": 1.0},
        "inputs": {"x": 1.0},
        "decision_inputs": {"x": 1.0},
        "event_time": now,
        "received_at": now,
        "source_event_id": "evt-1",
        "values": {"x": 1.0},
        "indicator_id": "indicator",
        "label": "neutral",
        "confidence": 0.5,
        "regime_id": "regime",
        "value": 1.0,
        "composition_id": "composition",
        "action": "hold",
        "strength": 0.5,
        "strategy_id": "strategy",
        "source": "provider",
        "observed_at": now,
        "content_digest": "sha256:abc",
        "decision_id": "decision",
        "approved": True,
        "exposure_fraction": 0.25,
        "risk_id": "risk",
        "symbol": "BTCUSDT",
        "payload_digest": "sha256:event",
    }
    if contract_type is IndicatorRequest:
        return contract_type(
            series=values["series"],
            event_time=now,
            received_at=now,
            source_event_id="evt-1",
        )
    if contract_type is IndicatorOutput:
        return contract_type(values["values"], now, "indicator")
    if contract_type is RegimeRequest:
        return contract_type(values["features"], now, now, "evt-1")
    if contract_type is RegimeOutput:
        return contract_type("neutral", 0.5, now, "regime")
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
    if contract_type is MarketEvent:
        return contract_type("evt-1", "provider", "BTCUSDT", now, now, "sha256:event")
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
