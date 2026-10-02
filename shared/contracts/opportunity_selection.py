"""FILE: shared/contracts/opportunity_selection.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Define deterministic selection of already-ranked eligible opportunities with market provenance.
LAYER: shared
OWNS: Immutable selection result semantics and market provenance.
DOES_NOT_OWN: ranking, safety approval, risk allocation, execution, persistence, or profitability claims.
DEPENDENCIES: dataclasses, shared.contracts.market_context, shared.contracts.opportunity_ranking
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from dataclasses import dataclass

from shared.contracts.market_context import MarketContext
from shared.contracts.opportunity_ranking import OpportunityRankingOutput

OPPORTUNITY_SELECTION_CONTRACT_ID = "opportunity_selection_boundary"
OPPORTUNITY_SELECTION_CONTRACT_VERSION = "1.2.0"


@dataclass(frozen=True, slots=True)
class OpportunitySelectionOutput:
    """Immutable deterministic ordering of eligible opportunities with market provenance."""

    selected: tuple[OpportunityRankingOutput, ...]
    selection_id: str
    market_context: MarketContext
    contract_version: str = OPPORTUNITY_SELECTION_CONTRACT_VERSION

    def __post_init__(self) -> None:
        if not self.selection_id.strip():
            raise ValueError("selection_id must not be empty")
        if any(not item.eligible for item in self.selected):
            raise ValueError("selection may contain eligible opportunities only")
        if any(
            left.rank_score < right.rank_score
            for left, right in zip(self.selected, self.selected[1:])
        ):
            raise ValueError("selected opportunities must be ordered by rank_score")
        if any(item.event_time != self.market_context.event_time for item in self.selected):
            raise ValueError("selected opportunity event_time must match market context")
