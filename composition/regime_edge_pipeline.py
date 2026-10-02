"""FILE: composition/regime_edge_pipeline.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Adapt canonical regime analysis into the existing confirmation-to-edge path.
LAYER: composition
OWNS: normalized descriptive regime-to-edge adaptation only.
DOES_NOT_OWN: regime analysis, confirmation generation, edge methodology, setup generation, cost/liquidity/risk approval, decision finalization, execution, persistence, or profitability claims.
DEPENDENCIES: analysis.regime_analysis, composition.confirmation_contract, composition.edge_evaluation_pipeline, shared.interfaces.setup
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from analysis.regime_analysis import RegimeAnalysisOutput
from composition.confirmation_contract import ConfirmationOutput
from composition.edge_evaluation_pipeline import EdgeEvaluationPipeline
from shared.contracts.edge_evaluation import EdgeEvaluationOutput
from shared.interfaces.setup import SetupOutput


class RegimeEdgeEvaluationPipeline:
    """Bind point-in-time regime analysis into the existing edge boundary."""

    def __init__(self, edge_pipeline: EdgeEvaluationPipeline | None = None) -> None:
        self._edge_pipeline = edge_pipeline or EdgeEvaluationPipeline()

    def evaluate(
        self,
        *,
        setup: SetupOutput,
        confirmation: ConfirmationOutput,
        regime: RegimeAnalysisOutput,
        liquidity_quality: float,
        cost_efficiency: float,
    ) -> EdgeEvaluationOutput:
        """Evaluate edge with normalized descriptive regime alignment."""
        if regime.event_time != confirmation.event_time:
            raise ValueError("regime event_time must match confirmation event_time")
        return self._edge_pipeline.evaluate(
            setup=setup,
            confirmation=confirmation,
            regime_alignment=self._regime_alignment(regime),
            liquidity_quality=liquidity_quality,
            cost_efficiency=cost_efficiency,
            event_time=regime.event_time,
        )

    @staticmethod
    def _regime_alignment(regime: RegimeAnalysisOutput) -> float:
        """Return directional-regime strength; non-directional regimes map to zero."""
        if regime.classification.label in {"trend_up", "trend_down"}:
            return regime.classification.confidence
        return 0.0
