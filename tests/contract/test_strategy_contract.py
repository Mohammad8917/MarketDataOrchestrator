"""FILE: tests/contract/test_strategy_contract.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify the canonical strategy evaluation contract invariants.
LAYER: tests
OWNS: Contract-level verification for strategy_evaluation_boundary.
DOES_NOT_OWN: strategy production behavior, decision finalization, risk
DEPENDENCIES: pytest; shared.interfaces.strategy
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timezone
from typing import Any

import pytest

from shared.interfaces.strategy import (
    STRATEGY_CONTRACT_VERSION,
    Strategy,
    StrategyOutput,
    StrategyRequest,
)


class FakeStrategy:
    contract_id = "strategy_evaluation_boundary"
    contract_version = STRATEGY_CONTRACT_VERSION
    strategy_id = "fake"

    def evaluate(self, request: StrategyRequest) -> StrategyOutput:
        return StrategyOutput("hold", 0.5, request.event_time, self.strategy_id)


def test_protocol_shape_is_runtime_checkable() -> None:
    assert isinstance(FakeStrategy(), Strategy)


def test_request_and_output_are_typed_and_immutable() -> None:
    now = datetime.now(timezone.utc)
    request = StrategyRequest({"signal": 0.7}, now, now, "evt-1")
    output = FakeStrategy().evaluate(request)
    assert output.contract_version == STRATEGY_CONTRACT_VERSION
    with pytest.raises(AttributeError):
        output.action = "buy"  # type: ignore[misc]


@pytest.mark.parametrize("field", ["event_time", "received_at"])
def test_request_rejects_naive_timestamps(field: str) -> None:
    now = datetime(2026, 9, 24, 10, 0)
    values: dict[str, Any] = {
        "inputs": {"signal": 0.7},
        "event_time": now.replace(tzinfo=timezone.utc),
        "received_at": now.replace(tzinfo=timezone.utc),
        "source_event_id": "evt-1",
    }
    values[field] = now
    with pytest.raises(ValueError, match="UTC"):
        StrategyRequest(**values)


def test_request_rejects_blank_source_event_id() -> None:
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError, match="source_event_id"):
        StrategyRequest({}, now, now, "")


def test_output_rejects_empty_action_and_strategy_id() -> None:
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError, match="action"):
        StrategyOutput("", 0.5, now, "fake")
    with pytest.raises(ValueError, match="strategy_id"):
        StrategyOutput("hold", 0.5, now, "")


@pytest.mark.parametrize("strength", [-0.1, 1.1])
def test_output_rejects_invalid_strength(strength: float) -> None:
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError, match="strength"):
        StrategyOutput("hold", strength, now, "fake")
