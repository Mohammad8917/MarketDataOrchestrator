"""FILE: decision/decision_audit.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Produce deterministic reconstruction metadata from completed decision-chain outputs.
LAYER: decision
OWNS: Audit identity construction and boundary-reference aggregation.
DOES_NOT_OWN: persistence, storage, signal generation, cost/liquidity/risk calculation, or execution.
DEPENDENCIES: hashlib, shared.contracts.decision_audit, shared.contracts.edge_evaluation, shared.contracts.market_context, shared.contracts.opportunity_ranking, shared.contracts.opportunity_selection, shared.contracts.pretrade_safety
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from hashlib import sha256

from shared.contracts.decision_audit import DecisionAuditRecord
from shared.contracts.edge_evaluation import EdgeEvaluationOutput
from shared.contracts.opportunity_ranking import OpportunityRankingOutput
from shared.contracts.opportunity_selection import OpportunitySelectionOutput
from shared.contracts.pretrade_safety import PreTradeSafetyOutput


class DecisionAuditRecorder:
    """Create immutable reconstruction metadata without persisting it."""

    contract_id = "decision_audit_boundary"
    contract_version = "1.2.0"

    def record(
        self,
        safety: PreTradeSafetyOutput,
        decision_id: str,
        cost_id: str,
        liquidity_id: str,
        risk_id: str,
        edge: EdgeEvaluationOutput | None = None,
        ranking: OpportunityRankingOutput | None = None,
        selection: OpportunitySelectionOutput | None = None,
    ) -> DecisionAuditRecord:
        """Aggregate canonical upstream IDs into a deterministic audit record."""
        if (edge is None) != (ranking is None) or (ranking is None) != (selection is None):
            raise ValueError("edge, ranking, and selection provenance must be supplied together")
        if edge is not None and ranking is not None and selection is not None:
            if edge.event_time != safety.event_time or ranking.event_time != safety.event_time:
                raise ValueError("opportunity provenance event_time must match safety")
            if ranking.ranking_id not in {item.ranking_id for item in selection.selected}:
                raise ValueError("ranking must be present in selection provenance")
        edge_id = edge.edge_id if edge is not None else None
        ranking_id = ranking.ranking_id if ranking is not None else None
        selection_id = selection.selection_id if selection is not None else None
        market_context = selection.market_context if selection is not None else None
        market_provenance = (
            f"{market_context.market}|{market_context.symbol}|{market_context.timeframe}|"
            f"{market_context.event_time.isoformat()}|{market_context.source_event_id}"
            if market_context is not None
            else ""
        )
        payload = (
            f"{decision_id}|{cost_id}|{liquidity_id}|{risk_id}|"
            f"{safety.safety_id}|{safety.action}|{','.join(safety.reasons)}|"
            f"{safety.event_time.isoformat()}|{edge_id or ''}|{ranking_id or ''}|"
            f"{selection_id or ''}|{market_provenance}"
        ).encode("utf-8")
        return DecisionAuditRecord(
            decision_id=decision_id,
            cost_id=cost_id,
            liquidity_id=liquidity_id,
            risk_id=risk_id,
            safety_id=safety.safety_id,
            action=safety.action,
            reasons=safety.reasons,
            event_time=safety.event_time,
            audit_id=sha256(payload).hexdigest(),
            edge_id=edge_id,
            ranking_id=ranking_id,
            selection_id=selection_id,
            market_context=market_context,
        )
