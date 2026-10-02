"""FILE: orchestrator/opportunity_orchestrator.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Assemble and invoke the application opportunity workflow at the composition root.
LAYER: orchestrator
OWNS: Concrete dependency wiring, immutable orchestration input assembly, and workflow delegation only.
DOES_NOT_OWN: analytical methodology, cost/liquidity estimation, ranking, selection, risk allocation, execution, persistence, or delivery.
DEPENDENCIES: analysis, app, composition, shared
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from dataclasses import dataclass

from analysis.regime_analysis import RegimeAnalysisOutput
from app.application import OpportunityApplication
from app.dependency_container import build_opportunity_application
from app.application_contract import ApplicationRequest
from composition.confirmation_contract import ConfirmationOutput
from composition.opportunity_chain_pipeline import ComposedOpportunityChainPipeline
from shared.contracts.cost import CostOutput
from shared.contracts.liquidity import LiquidityOutput
from shared.contracts.market_context import MarketContext
from shared.contracts.opportunity_selection import OpportunitySelectionOutput
from shared.contracts.pretrade_safety import PreTradeSafetyOutput
from shared.interfaces.setup import SetupOutput
from shared.models.decision import DecisionOutput


@dataclass(frozen=True, slots=True)
class OpportunityOrchestrationInput:
    """Immutable concrete input assembled from canonical upstream boundaries."""

    market_context: MarketContext
    decision: DecisionOutput
    safety: PreTradeSafetyOutput
    setup: SetupOutput
    confirmation: ConfirmationOutput
    regime: RegimeAnalysisOutput
    cost: CostOutput
    liquidity: LiquidityOutput
    liquidity_quality: float
    cost_efficiency: float
    limit: int

    def __post_init__(self) -> None:
        if self.market_context.event_time != self.regime.event_time:
            raise ValueError("market context event_time must match regime event_time")
        if not 0.0 <= self.liquidity_quality <= 1.0:
            raise ValueError("liquidity_quality must be between 0 and 1")
        if not 0.0 <= self.cost_efficiency <= 1.0:
            raise ValueError("cost_efficiency must be between 0 and 1")
        if self.limit < 1:
            raise ValueError("limit must be at least 1")


class OpportunityOrchestrator:
    """Own the concrete composition root and delegate execution to application."""

    def __init__(self, application: OpportunityApplication[OpportunityOrchestrationInput]) -> None:
        self._application = application

    def run(self, request: OpportunityOrchestrationInput) -> OpportunitySelectionOutput:
        """Delegate one immutable workflow request without recalculating analytical results."""
        return self._application.run(ApplicationRequest(payload=request, limit=request.limit))


def build_opportunity_orchestrator() -> OpportunityOrchestrator:
    """Construct the production opportunity workflow dependency graph exactly once."""
    pipeline = ComposedOpportunityChainPipeline()

    def evaluate(request: OpportunityOrchestrationInput, limit: int) -> OpportunitySelectionOutput:
        return pipeline.evaluate(
            decision=request.decision,
            safety=request.safety,
            setup=request.setup,
            confirmation=request.confirmation,
            regime=request.regime,
            cost=request.cost,
            liquidity=request.liquidity,
            liquidity_quality=request.liquidity_quality,
            cost_efficiency=request.cost_efficiency,
            limit=limit,
        )

    return OpportunityOrchestrator(build_opportunity_application(evaluate))
