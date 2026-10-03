"""FILE: analysis/opportunity_chain_pipeline.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Compose the canonical edge, safety, ranking, and selection boundaries into one analysis-layer flow.
LAYER: analysis
OWNS: Deterministic boundary composition only.
DOES_NOT_OWN: signal generation, safety approval, edge recalculation, ranking methodology, risk allocation, execution, persistence, or profitability claims.
DEPENDENCIES: analysis.opportunity_ranking_pipeline, analysis.opportunity_selection_pipeline, shared.contracts.edge_evaluation, shared.contracts.market_context, shared.contracts.pretrade_safety, shared.models.decision
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from analysis.opportunity_ranking_pipeline import OpportunityRankingPipeline
from analysis.opportunity_selection_pipeline import OpportunitySelectionPipeline
from shared.contracts.edge_evaluation import EdgeEvaluationOutput
from shared.contracts.market_context import MarketContext
from shared.contracts.pretrade_safety import PreTradeSafetyOutput
from shared.contracts.opportunity_selection import OpportunitySelectionOutput
from shared.models.decision import DecisionOutput


def _require_instance[T](value: object, expected: type[T], name: str) -> T:
    """Reject invalid runtime inputs before delegated boundary access."""
    if not isinstance(value, expected):
        raise ValueError(f"{name} must be an instance of {expected.__name__}")
    return value


def _require_positive_limit(value: object) -> int:
    """Reject bool and non-integer limits before selection delegation."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("limit must be a positive integer")
    if value < 1:
        raise ValueError("limit must be positive")
    return value


class OpportunityChainPipeline:
    """Compose existing canonical opportunity boundaries without recalculation."""

    def __init__(
        self,
        ranking_pipeline: OpportunityRankingPipeline | None = None,
        selection_pipeline: OpportunitySelectionPipeline | None = None,
    ) -> None:
        self._ranking = ranking_pipeline or OpportunityRankingPipeline()
        self._selection = selection_pipeline or OpportunitySelectionPipeline()

    def evaluate(
        self,
        decision: DecisionOutput,
        safety: PreTradeSafetyOutput,
        edge: EdgeEvaluationOutput,
        limit: int,
        market_context: MarketContext,
    ) -> OpportunitySelectionOutput:
        """Produce selected opportunities from already-evaluated canonical values."""
        validated_decision = _require_instance(decision, DecisionOutput, "decision")
        validated_safety = _require_instance(safety, PreTradeSafetyOutput, "safety")
        validated_edge = _require_instance(edge, EdgeEvaluationOutput, "edge")
        validated_context = _require_instance(market_context, MarketContext, "market_context")
        validated_limit = _require_positive_limit(limit)
        ranking = self._ranking.rank(validated_decision, validated_safety, validated_edge)
        return self._selection.select((ranking,), validated_limit, validated_context)
