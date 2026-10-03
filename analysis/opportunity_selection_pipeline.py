"""FILE: analysis/opportunity_selection_pipeline.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Integrate canonical opportunity rankings into deterministic selection.
LAYER: analysis
OWNS: Boundary adaptation into the opportunity-selection consumer.
DOES_NOT_OWN: ranking, safety approval, risk allocation, execution, persistence, or profitability claims.
DEPENDENCIES: analysis.opportunity_selector, shared.contracts.market_context, shared.contracts.opportunity_ranking, shared.contracts.opportunity_selection
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from analysis.opportunity_selector import OpportunitySelector
from shared.contracts.market_context import MarketContext
from shared.contracts.opportunity_ranking import OpportunityRankingOutput
from shared.contracts.opportunity_selection import (
    OPPORTUNITY_SELECTION_CONTRACT_ID,
    OPPORTUNITY_SELECTION_CONTRACT_VERSION,
    OpportunitySelectionOutput,
)


class OpportunitySelectionPipeline:
    """Adapt canonical rankings into the deterministic selection boundary."""

    contract_id = OPPORTUNITY_SELECTION_CONTRACT_ID
    contract_version = OPPORTUNITY_SELECTION_CONTRACT_VERSION

    def __init__(self, selector: OpportunitySelector | None = None) -> None:
        self._selector = selector or OpportunitySelector()

    def select(
        self,
        rankings: tuple[OpportunityRankingOutput, ...],
        limit: int,
        market_context: MarketContext,
    ) -> OpportunitySelectionOutput:
        """Select from existing rankings without recomputing upstream decisions."""
        if not isinstance(rankings, tuple):
            raise ValueError("rankings must be a tuple")
        if isinstance(limit, bool) or not isinstance(limit, int):
            raise ValueError("limit must be a positive integer")
        if limit < 1:
            raise ValueError("limit must be positive")
        if not isinstance(market_context, MarketContext):
            raise ValueError("market_context must be an instance of MarketContext")
        if any(not isinstance(item, OpportunityRankingOutput) for item in rankings):
            raise ValueError("rankings must contain OpportunityRankingOutput instances")
        return self._selector.select(rankings, limit, market_context)
