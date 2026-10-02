"""FILE: cost/cost_engine.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Apply a deterministic cost gate to supplied spread, slippage, and fee observations.
LAYER: cost
OWNS: Cost aggregation and hard cost acceptance boundary.
DOES_NOT_OWN: cost estimation, market-data I/O, liquidity, risk sizing, decision generation, persistence, or execution.
DEPENDENCIES: shared.contracts.cost
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from hashlib import sha256

from shared.contracts.cost import CostOutput, CostRequest

_COST_FIELDS = ("spread_fraction", "slippage_fraction", "fee_fraction")


class DeterministicCostEngine:
    """Aggregate bounded supplied cost observations and apply a hard ceiling."""

    contract_id = "cost_evaluation_boundary"
    contract_version = "1.0.0"

    def evaluate(self, request: CostRequest) -> CostOutput:
        """Evaluate total supplied transaction cost without estimating missing inputs."""
        total = sum(getattr(request, field) for field in _COST_FIELDS)
        approved = total <= request.max_cost_fraction
        return CostOutput(
            approved=approved,
            total_cost_fraction=total,
            event_time=request.event_time,
            cost_id=self._cost_id(request, total, approved),
        )

    @staticmethod
    def _cost_id(request: CostRequest, total: float, approved: bool) -> str:
        payload = (
            f"{request.source_event_id}|{request.event_time.isoformat()}|"
            f"{total:.12f}|{approved}"
        ).encode("utf-8")
        return sha256(payload).hexdigest()
