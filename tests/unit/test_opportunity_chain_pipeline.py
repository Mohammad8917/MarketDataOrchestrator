"""Adversarial tests for the direct opportunity-chain boundary."""

from datetime import UTC, datetime
from typing import Any

import pytest

from analysis.opportunity_chain_pipeline import OpportunityChainPipeline
from shared.contracts.edge_evaluation import EdgeEvaluationOutput
from shared.contracts.market_context import MarketContext
from shared.contracts.pretrade_safety import PreTradeSafetyOutput
from shared.models.decision import DecisionOutput

NOW = datetime(2026, 10, 3, 13, tzinfo=UTC)
CONTEXT = MarketContext("Crypto", "BTCUSDT", "1h", NOW, "evt-1")


def _decision() -> DecisionOutput:
    return DecisionOutput("BUY", 0.9, NOW, "decision-1")


def _safety() -> PreTradeSafetyOutput:
    return PreTradeSafetyOutput(True, "BUY", 0.2, (), NOW, "safety-1")


def _edge() -> EdgeEvaluationOutput:
    return EdgeEvaluationOutput(0.7, NOW, "edge-1")


def _evaluate(**overrides: Any):
    values: dict[str, Any] = {
        "decision": _decision(),
        "safety": _safety(),
        "edge": _edge(),
        "limit": 1,
        "market_context": CONTEXT,
    }
    values.update(overrides)
    return OpportunityChainPipeline().evaluate(**values)


def test_chain_reaches_selection_from_canonical_inputs() -> None:
    output = _evaluate()
    assert len(output.selected) == 1
    assert output.selected[0].action == "BUY"
    assert output.selected[0].source_safety_id == "safety-1"
    assert output.selected[0].source_edge_id == "edge-1"
    assert output.market_context == CONTEXT


@pytest.mark.parametrize("field", ["decision", "safety", "edge", "market_context"])
def test_chain_rejects_wrong_runtime_object_types(field: str) -> None:
    with pytest.raises(ValueError, match=field):
        _evaluate(**{field: None})


@pytest.mark.parametrize("limit", [True, False, 1.0, "1", None])
def test_chain_rejects_invalid_limit_types(limit: object) -> None:
    with pytest.raises(ValueError, match="limit"):
        _evaluate(limit=limit)


@pytest.mark.parametrize("limit", [0, -1])
def test_chain_rejects_non_positive_limit(limit: int) -> None:
    with pytest.raises(ValueError, match="limit must be positive"):
        _evaluate(limit=limit)
