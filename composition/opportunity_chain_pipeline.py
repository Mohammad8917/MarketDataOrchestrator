"""FILE: composition/opportunity_chain_pipeline.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Compose canonical cost/liquidity edge evaluation with opportunity ranking and selection.
LAYER: composition
OWNS: Deterministic cross-layer boundary composition only.
DOES_NOT_OWN: cost/liquidity estimation, regime analysis, edge methodology, safety approval, ranking methodology, selection methodology, risk allocation, execution, persistence, or profitability claims.
DEPENDENCIES: analysis.opportunity_chain_pipeline, composition.cost_liquidity_edge_pipeline, shared.contracts.cost, shared.contracts.liquidity, shared.contracts.market_context, shared.contracts.opportunity_selection, shared.contracts.pretrade_safety, shared.models.decision
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

import math

from analysis.opportunity_chain_pipeline import OpportunityChainPipeline
from analysis.regime_analysis import RegimeAnalysisOutput
from composition.confirmation_contract import ConfirmationOutput
from composition.cost_liquidity_edge_pipeline import CostLiquidityEdgeEvaluationPipeline
from shared.contracts.cost import CostOutput
from shared.contracts.liquidity import LiquidityOutput
from shared.contracts.market_context import MarketContext
from shared.contracts.opportunity_selection import OpportunitySelectionOutput
from shared.contracts.pretrade_safety import PreTradeSafetyOutput
from shared.interfaces.setup import SetupOutput
from shared.models.decision import DecisionOutput


def _require_instance(value: object, expected: type[object], name: str) -> None:
    if not isinstance(value, expected):
        raise ValueError(f"{name} must be a {expected.__name__}")


def _require_finite_fraction(value: object, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric")
    numeric = float(value)
    if not math.isfinite(numeric) or not 0.0 <= numeric <= 1.0:
        raise ValueError(f"{name} must be finite and between 0 and 1")


class ComposedOpportunityChainPipeline:
    """Compose the canonical cost/liquidity edge and opportunity-chain boundaries."""

    def __init__(
        self,
        edge_pipeline: CostLiquidityEdgeEvaluationPipeline | None = None,
        opportunity_pipeline: OpportunityChainPipeline | None = None,
    ) -> None:
        self._edge = edge_pipeline or CostLiquidityEdgeEvaluationPipeline()
        self._opportunity = opportunity_pipeline or OpportunityChainPipeline()

    def evaluate(
        self,
        *,
        decision: DecisionOutput,
        safety: PreTradeSafetyOutput,
        setup: SetupOutput,
        confirmation: ConfirmationOutput,
        regime: RegimeAnalysisOutput,
        cost: CostOutput,
        liquidity: LiquidityOutput,
        liquidity_quality: float,
        cost_efficiency: float,
        limit: int,
        market_context: MarketContext,
    ) -> OpportunitySelectionOutput:
        """Produce selected opportunities from canonical upstream observations."""
        for value, expected, name in (
            (decision, DecisionOutput, "decision"),
            (safety, PreTradeSafetyOutput, "safety"),
            (setup, SetupOutput, "setup"),
            (confirmation, ConfirmationOutput, "confirmation"),
            (regime, RegimeAnalysisOutput, "regime"),
            (cost, CostOutput, "cost"),
            (liquidity, LiquidityOutput, "liquidity"),
            (market_context, MarketContext, "market_context"),
        ):
            _require_instance(value, expected, name)
        _require_finite_fraction(liquidity_quality, "liquidity_quality")
        _require_finite_fraction(cost_efficiency, "cost_efficiency")
        if isinstance(limit, bool) or not isinstance(limit, int):
            raise ValueError("limit must be an integer")
        if limit < 1:
            raise ValueError("limit must be at least 1")
        event_time = market_context.event_time
        aligned_inputs = (
            ("decision", decision.event_time),
            ("safety", safety.event_time),
            ("setup", setup.event_time),
            ("confirmation", confirmation.event_time),
            ("regime", regime.event_time),
            ("cost", cost.event_time),
            ("liquidity", liquidity.event_time),
        )
        for name, candidate in aligned_inputs:
            if candidate != event_time:
                raise ValueError(f"{name} event_time must match market context event_time")
        if market_context.source_event_id != regime.source_event_id:
            raise ValueError("market context source_event_id must match regime source_event_id")
        edge = self._edge.evaluate(
            setup=setup,
            confirmation=confirmation,
            regime=regime,
            cost=cost,
            liquidity=liquidity,
            liquidity_quality=liquidity_quality,
            cost_efficiency=cost_efficiency,
        )
        return self._opportunity.evaluate(decision, safety, edge, limit, market_context)
