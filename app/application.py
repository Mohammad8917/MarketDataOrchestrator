"""FILE: app/application.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Orchestrate the canonical composed opportunity chain at application boundary.
LAYER: app
OWNS: Lifecycle invocation and dependency delegation only.
DOES_NOT_OWN: analytical methodology, cost/liquidity estimation, safety approval, ranking, selection, risk allocation, execution, persistence, or delivery.
DEPENDENCIES: app.application_contract, composition.opportunity_chain_pipeline, shared.contracts.opportunity_selection
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from composition.opportunity_chain_pipeline import ComposedOpportunityChainPipeline
from shared.contracts.opportunity_selection import OpportunitySelectionOutput

from app.application_contract import ApplicationRequest


class OpportunityApplication:
    """Invoke the canonical opportunity chain without owning analytical behavior."""

    def __init__(self, pipeline: ComposedOpportunityChainPipeline | None = None) -> None:
        self._pipeline = pipeline or ComposedOpportunityChainPipeline()

    def run(self, request: ApplicationRequest) -> OpportunitySelectionOutput:
        """Delegate one immutable request to the canonical composition boundary."""
        return self._pipeline.evaluate(
            decision=request.decision,
            safety=request.safety,
            setup=request.setup,
            confirmation=request.confirmation,
            regime=request.regime,
            cost=request.cost,
            liquidity=request.liquidity,
            liquidity_quality=request.liquidity_quality,
            cost_efficiency=request.cost_efficiency,
            limit=request.limit,
        )
