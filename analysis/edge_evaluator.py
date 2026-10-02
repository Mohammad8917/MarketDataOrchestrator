"""FILE: analysis/edge_evaluator.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Produce a deterministic descriptive edge score from normalized upstream analytical components.
LAYER: analysis
OWNS: Edge scoring methodology and immutable output construction.
DOES_NOT_OWN: setup/confirmation generation, market-data ingestion, cost/liquidity/risk approval, decision finalization, execution, persistence, calibration, or profitability claims.
DEPENDENCIES: hashlib, shared.contracts.edge_evaluation
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from hashlib import sha256

from shared.contracts.edge_evaluation import EdgeEvaluationOutput, EdgeEvaluationRequest


class DeterministicEdgeEvaluator:
    """Calculate a descriptive normalized edge score.

    The v1 methodology is an equal-weight mean of five already-normalized
    components. The result is an ordering feature, not a probability,
    expected return, or profitability guarantee.
    """

    contract_id = "edge_evaluation_boundary"
    contract_version = "1.0.0"

    def evaluate(self, request: EdgeEvaluationRequest) -> EdgeEvaluationOutput:
        components = (
            request.setup_quality,
            request.confirmation_strength,
            request.regime_alignment,
            request.liquidity_quality,
            request.cost_efficiency,
        )
        edge_score = sum(components) / len(components)
        return EdgeEvaluationOutput(
            edge_score=edge_score,
            event_time=request.event_time,
            edge_id=self._edge_id(request, edge_score),
        )

    @staticmethod
    def _edge_id(request: EdgeEvaluationRequest, edge_score: float) -> str:
        payload = (
            f"{request.source_setup_id}|{request.source_confirmation_id}|"
            f"{request.setup_quality:.12f}|{request.confirmation_strength:.12f}|"
            f"{request.regime_alignment:.12f}|{request.liquidity_quality:.12f}|"
            f"{request.cost_efficiency:.12f}|{edge_score:.12f}"
        ).encode("utf-8")
        return sha256(payload).hexdigest()
