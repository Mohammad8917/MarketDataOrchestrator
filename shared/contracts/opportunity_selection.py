"""FILE: shared/contracts/opportunity_selection.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 2026-10-03
DATE_GREGORIAN: 2026-10-03
DATE_PERSIAN: 1405-07-11
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
        if not isinstance(self.selected, tuple):
            raise ValueError("selected must be a tuple")
        if any(type(item) is not OpportunityRankingOutput for item in self.selected):
            raise ValueError("selected must contain only OpportunityRankingOutput values")
        if not isinstance(self.selection_id, str):
            raise ValueError("selection_id must be a string")
        if not self.selection_id.strip():
            raise ValueError("selection_id must not be empty")
        if not isinstance(self.market_context, MarketContext):
            raise ValueError("market_context must be a MarketContext")
        if not isinstance(self.contract_version, str):
            raise ValueError("contract_version must be a string")
        if not self.contract_version.strip():
            raise ValueError("contract_version must not be empty")
        if any(not item.eligible for item in self.selected):
            raise ValueError("selection may contain eligible opportunities only")
        ranking_ids = [item.ranking_id for item in self.selected]
        if len(ranking_ids) != len(set(ranking_ids)):
            raise ValueError("selected ranking_id values must be unique")
        if any(
            left.rank_score < right.rank_score
            for left, right in zip(self.selected, self.selected[1:])
        ):
            raise ValueError("selected opportunities must be ordered by rank_score")
        if any(item.event_time != self.market_context.event_time for item in self.selected):
            raise ValueError("selected opportunity event_time must match market context")
