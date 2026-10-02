"""FILE: composition/cost_liquidity_edge_pipeline.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Bind canonical CostOutput and LiquidityOutput gates into the existing regime-to-edge path.
LAYER: composition
OWNS: point-in-time cost/liquidity gate adaptation into edge evaluation only.
DOES_NOT_OWN: cost estimation, liquidity estimation, regime analysis, setup/confirmation generation, edge methodology, risk approval, decision finalization, execution, persistence, or profitability claims.
DEPENDENCIES: analysis.regime_analysis, composition.confirmation_contract, composition.regime_edge_pipeline, shared.contracts.cost, shared.contracts.liquidity, shared.interfaces.setup
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from shared.contracts.cost import CostOutput
from shared.contracts.edge_evaluation import EdgeEvaluationOutput
from shared.contracts.liquidity import LiquidityOutput
from shared.interfaces.setup import SetupOutput
from analysis.regime_analysis import RegimeAnalysisOutput
from composition.confirmation_contract import ConfirmationOutput
from composition.regime_edge_pipeline import RegimeEdgeEvaluationPipeline


class CostLiquidityEdgeEvaluationPipeline:
    """Bind approved cost/liquidity observations to the canonical regime-to-edge path."""

    def __init__(
        self,
        edge_pipeline: RegimeEdgeEvaluationPipeline | None = None,
    ) -> None:
        self._edge_pipeline = edge_pipeline or RegimeEdgeEvaluationPipeline()

    def evaluate(
        self,
        *,
        setup: SetupOutput,
        confirmation: ConfirmationOutput,
        regime: RegimeAnalysisOutput,
        cost: CostOutput,
        liquidity: LiquidityOutput,
        liquidity_quality: float,
        cost_efficiency: float,
    ) -> EdgeEvaluationOutput:
        """Evaluate edge only when canonical cost/liquidity gates are approved and aligned."""
        event_time = regime.event_time
        if cost.event_time != event_time:
            raise ValueError("cost event_time must match edge evaluation event_time")
        if liquidity.event_time != event_time:
            raise ValueError("liquidity event_time must match edge evaluation event_time")
        if not cost.approved:
            raise ValueError("cost must be approved before edge evaluation")
        if not liquidity.approved:
            raise ValueError("liquidity must be approved before edge evaluation")
        return self._edge_pipeline.evaluate(
            setup=setup,
            confirmation=confirmation,
            regime=regime,
            liquidity_quality=liquidity_quality,
            cost_efficiency=cost_efficiency,
        )
