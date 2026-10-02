"""FILE: decision/opportunity_chain_audit.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Adapt the completed opportunity chain into the canonical decision-audit boundary.
LAYER: decision
OWNS: Audit-boundary adaptation only.
DOES_NOT_OWN: ranking, selection, safety approval, edge calculation, persistence, execution, or profitability claims.
DEPENDENCIES: decision.decision_audit, shared.contracts.edge_evaluation, shared.contracts.opportunity_ranking, shared.contracts.opportunity_selection, shared.contracts.pretrade_safety
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from shared.contracts.decision_audit import DecisionAuditRecord
from shared.contracts.edge_evaluation import EdgeEvaluationOutput
from shared.contracts.opportunity_ranking import OpportunityRankingOutput
from shared.contracts.opportunity_selection import OpportunitySelectionOutput
from shared.contracts.pretrade_safety import PreTradeSafetyOutput
from decision.decision_audit import DecisionAuditRecorder


class OpportunityChainAuditRecorder:
    """Bind complete opportunity provenance to the existing audit methodology."""

    def __init__(self, recorder: DecisionAuditRecorder | None = None) -> None:
        self._recorder = recorder or DecisionAuditRecorder()

    def record(
        self,
        *,
        safety: PreTradeSafetyOutput,
        decision_id: str,
        cost_id: str,
        liquidity_id: str,
        risk_id: str,
        edge: EdgeEvaluationOutput,
        ranking: OpportunityRankingOutput,
        selection: OpportunitySelectionOutput,
    ) -> DecisionAuditRecord:
        """Record audit metadata from a complete opportunity chain."""
        return self._recorder.record(
            safety,
            decision_id,
            cost_id,
            liquidity_id,
            risk_id,
            edge=edge,
            ranking=ranking,
            selection=selection,
        )
