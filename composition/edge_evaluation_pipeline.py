"""FILE: composition/edge_evaluation_pipeline.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Adapt canonical SetupOutput and ConfirmationOutput into the existing edge-evaluation request boundary.
LAYER: composition
OWNS: point-in-time setup-and-confirmation-to-edge adaptation only.
DOES_NOT_OWN: setup/confirmation generation, edge methodology, regime generation, cost/liquidity/risk approval, decision finalization, execution, persistence, or profitability claims.
DEPENDENCIES: analysis.edge_evaluator, composition.confirmation_contract, shared.contracts.edge_evaluation, shared.interfaces.setup
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from datetime import datetime

from analysis.edge_evaluator import DeterministicEdgeEvaluator
from composition.confirmation_contract import ConfirmationOutput
from shared.contracts.edge_evaluation import EdgeEvaluationOutput, EdgeEvaluationRequest
from shared.interfaces.setup import SetupOutput


class EdgeEvaluationPipeline:
    """Bind canonical setup and confirmation provenance to the existing edge methodology."""

    def __init__(self, evaluator: DeterministicEdgeEvaluator | None = None) -> None:
        self._evaluator = evaluator or DeterministicEdgeEvaluator()

    def evaluate(
        self,
        *,
        setup: SetupOutput,
        confirmation: ConfirmationOutput,
        regime_alignment: float,
        liquidity_quality: float,
        cost_efficiency: float,
        event_time: datetime,
    ) -> EdgeEvaluationOutput:
        """Evaluate edge only from valid setup and confirmed point-in-time confirmation."""
        if setup.direction == "neutral":
            raise ValueError("setup must be directional before edge evaluation")
        if setup.event_time != event_time:
            raise ValueError("setup event_time must match edge evaluation event_time")
        if confirmation.event_time != event_time:
            raise ValueError("confirmation event_time must match edge evaluation event_time")
        if not confirmation.confirmed:
            raise ValueError("confirmation must be confirmed before edge evaluation")
        request = EdgeEvaluationRequest(
            setup_quality=setup.strength,
            confirmation_strength=abs(confirmation.score),
            regime_alignment=regime_alignment,
            liquidity_quality=liquidity_quality,
            cost_efficiency=cost_efficiency,
            event_time=confirmation.event_time,
            source_setup_id=setup.setup_id,
            source_confirmation_id=confirmation.confirmation_id,
        )
        return self._evaluator.evaluate(request)
