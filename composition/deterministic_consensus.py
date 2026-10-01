"""FILE: composition/deterministic_consensus.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-01
DATE_PERSIAN: 1405-07-09
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Provide deterministic, market-agnostic signal confirmation by directional consensus.
LAYER: composition
OWNS: Sign-based consensus scoring and confirmation state for normalized analytical evidence.
DOES_NOT_OWN: signal generation, market-data I/O, persistence, regime semantics, timeframe semantics, cost, risk, decision finalization, trading actions
DEPENDENCIES: composition.confirmation_contract
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0

Methodology v1:
- Each upstream signal is normalized evidence in [-1.0, 1.0].
- Positive values cast positive directional votes; negative values cast negative votes; zero is neutral.
- The confirmation score is the net directional vote ratio: (positive_votes - negative_votes) / total_signals.
- Confirmation is true when the absolute score is at least 0.5.
- Empty evidence and out-of-range/non-finite values are invalid.
- No market, provider, timeframe, execution, cost, risk, or decision semantics are embedded here.
- A confirmed result is analytical confirmation only and is not a trading instruction or profitability claim.
"""

from math import isfinite

from composition.confirmation_contract import (
    CONFIRMATION_CONTRACT_ID,
    CONFIRMATION_CONTRACT_VERSION,
    ConfirmationOutput,
    ConfirmationRequest,
)

CONFIRMATION_METHODOLOGY_ID = "deterministic_directional_consensus_v1"
CONFIRMATION_METHODOLOGY_VERSION = "1.0.0"
CONFIRMATION_THRESHOLD = 0.5


class DeterministicDirectionalConsensus:
    """Confirm normalized evidence using deterministic directional consensus."""

    contract_id = CONFIRMATION_CONTRACT_ID
    contract_version = CONFIRMATION_CONTRACT_VERSION
    confirmation_id = CONFIRMATION_METHODOLOGY_ID

    def confirm(self, request: ConfirmationRequest) -> ConfirmationOutput:
        if not request.signals:
            raise ValueError("signals must not be empty")

        positive = 0
        negative = 0
        for value in request.signals.values():
            if not isfinite(value):
                raise ValueError("signals must contain only finite values")
            if not -1.0 <= value <= 1.0:
                raise ValueError("signals must be within [-1.0, 1.0]")
            if value > 0.0:
                positive += 1
            elif value < 0.0:
                negative += 1

        score = (positive - negative) / len(request.signals)
        return ConfirmationOutput(
            confirmed=abs(score) >= CONFIRMATION_THRESHOLD,
            score=score,
            event_time=request.event_time,
            confirmation_id=f"{request.source_event_id}:{self.confirmation_id}",
        )
