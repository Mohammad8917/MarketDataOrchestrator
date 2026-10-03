"""FILE: analysis/opportunity_selector.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Select a bounded deterministic subset of already-ranked eligible opportunities.
LAYER: analysis
OWNS: Eligibility filtering, deterministic ordering, and selection-limit enforcement.
DOES_NOT_OWN: ranking, cost/liquidity/risk evaluation, safety approval, execution, persistence, or profitability claims.
DEPENDENCIES: hashlib, shared.contracts.market_context, shared.contracts.opportunity_ranking, shared.contracts.opportunity_selection
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from hashlib import sha256

from shared.contracts.market_context import MarketContext
from shared.contracts.opportunity_ranking import OpportunityRankingOutput
from shared.contracts.opportunity_selection import (
    OPPORTUNITY_SELECTION_CONTRACT_VERSION,
    OpportunitySelectionOutput,
)


class OpportunitySelector:
    """Select and order eligible opportunities without changing their scores."""

    contract_id = "opportunity_selection_boundary"
    contract_version = OPPORTUNITY_SELECTION_CONTRACT_VERSION

    def select(
        self,
        rankings: tuple[OpportunityRankingOutput, ...],
        limit: int,
        market_context: MarketContext,
    ) -> OpportunitySelectionOutput:
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
        if any(item.event_time != market_context.event_time for item in rankings):
            raise ValueError("ranking event_time must match market context")
        eligible = tuple(item for item in rankings if item.eligible)
        ordered = tuple(
            sorted(
                eligible,
                key=lambda item: (-item.rank_score, item.ranking_id),
            )[:limit]
        )
        selection_id = self._selection_id(ordered, market_context)
        return OpportunitySelectionOutput(
            selected=ordered,
            selection_id=selection_id,
            market_context=market_context,
        )

    @staticmethod
    def _selection_id(
        selected: tuple[OpportunityRankingOutput, ...],
        market_context: MarketContext,
    ) -> str:
        context = "|".join(
            (
                market_context.market,
                market_context.symbol,
                market_context.timeframe,
                market_context.event_time.isoformat(),
                market_context.source_event_id,
            )
        )
        payload = "|".join((context, *(item.ranking_id for item in selected))).encode("utf-8")
        return sha256(payload).hexdigest()
