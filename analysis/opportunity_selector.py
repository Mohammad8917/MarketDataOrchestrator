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
DEPENDENCIES: shared.contracts.opportunity_ranking, shared.contracts.opportunity_selection
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from hashlib import sha256

from shared.contracts.opportunity_ranking import OpportunityRankingOutput
from shared.contracts.opportunity_selection import OpportunitySelectionOutput


class OpportunitySelector:
    """Select and order eligible opportunities without changing their scores."""

    contract_id = "opportunity_selection_boundary"
    contract_version = "1.1.0"

    def select(
        self,
        rankings: tuple[OpportunityRankingOutput, ...],
        limit: int,
    ) -> OpportunitySelectionOutput:
        if limit < 1:
            raise ValueError("limit must be positive")
        eligible = tuple(item for item in rankings if item.eligible)
        ordered = tuple(
            sorted(
                eligible,
                key=lambda item: (-item.rank_score, item.ranking_id),
            )[:limit]
        )
        selection_id = self._selection_id(ordered)
        return OpportunitySelectionOutput(selected=ordered, selection_id=selection_id)

    @staticmethod
    def _selection_id(selected: tuple[OpportunityRankingOutput, ...]) -> str:
        payload = "|".join(item.ranking_id for item in selected).encode("utf-8")
        return sha256(payload).hexdigest()
