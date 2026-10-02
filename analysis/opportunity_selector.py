"""Deterministic selection of already-ranked eligible opportunities."""

from shared.contracts.opportunity_ranking import OpportunityRankingOutput
from shared.contracts.opportunity_selection import OpportunitySelectionOutput


class OpportunitySelector:
    """Select and order eligible opportunities without changing their scores."""

    contract_id = "opportunity_selection_boundary"
    contract_version = "1.0.0"

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
        return OpportunitySelectionOutput(selected=ordered)
