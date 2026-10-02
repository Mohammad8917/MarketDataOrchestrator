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
DEPENDENCIES: analysis.opportunity_chain_pipeline, composition.cost_liquidity_edge_pipeline, shared.contracts.cost, shared.contracts.liquidity, shared.contracts.opportunity_selection, shared.contracts.pretrade_safety, shared.models.decision
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from analysis.opportunity_chain_pipeline import OpportunityChainPipeline
from analysis.regime_analysis import RegimeAnalysisOutput
from composition.confirmation_contract import ConfirmationOutput
from composition.cost_liquidity_edge_pipeline import CostLiquidityEdgeEvaluationPipeline
from shared.contracts.cost import CostOutput
from shared.contracts.liquidity import LiquidityOutput
from shared.contracts.opportunity_selection import OpportunitySelectionOutput
from shared.contracts.pretrade_safety import PreTradeSafetyOutput
from shared.interfaces.setup import SetupOutput
from shared.models.decision import DecisionOutput


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
    ) -> OpportunitySelectionOutput:
        """Produce selected opportunities from canonical upstream observations."""
        edge = self._edge.evaluate(
            setup=setup,
            confirmation=confirmation,
            regime=regime,
            cost=cost,
            liquidity=liquidity,
            liquidity_quality=liquidity_quality,
            cost_efficiency=cost_efficiency,
        )
        return self._opportunity.evaluate(decision, safety, edge, limit)
