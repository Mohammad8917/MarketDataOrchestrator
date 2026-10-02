"""FILE: liquidity/liquidity_engine.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Apply deterministic hard liquidity and participation gates to supplied observations.
LAYER: liquidity
OWNS: Liquidity sufficiency and participation acceptance boundary.
DOES_NOT_OWN: liquidity estimation, market-data I/O, cost estimation, risk sizing, decision generation, persistence, or execution.
DEPENDENCIES: hashlib, shared.contracts.liquidity
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from hashlib import sha256

from shared.contracts.liquidity import LiquidityOutput, LiquidityRequest


class DeterministicLiquidityEngine:
    """Apply supplied depth and participation ceilings without estimating liquidity."""

    contract_id = "liquidity_evaluation_boundary"
    contract_version = "1.0.0"

    def evaluate(self, request: LiquidityRequest) -> LiquidityOutput:
        """Approve only when observed depth and participation constraints both pass."""
        approved = (
            request.available_depth_fraction >= request.required_depth_fraction
            and request.requested_participation_fraction <= request.max_participation_fraction
        )
        return LiquidityOutput(
            approved=approved,
            event_time=request.event_time,
            liquidity_id=self._liquidity_id(request, approved),
        )

    @staticmethod
    def _liquidity_id(request: LiquidityRequest, approved: bool) -> str:
        payload = (f"{request.source_event_id}|{request.event_time.isoformat()}|{approved}").encode(
            "utf-8"
        )
        return sha256(payload).hexdigest()
