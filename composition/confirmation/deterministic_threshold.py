"""FILE: composition/confirmation/deterministic_threshold.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Provide a deterministic market-agnostic confirmation methodology over normalized signals.
LAYER: composition
OWNS: Equal-weight confirmation score and deterministic confirmation threshold.
DOES_NOT_OWN: signal generation, cost, liquidity, risk, decision finalization, trading actions, provider I/O, persistence
DEPENDENCIES: composition.confirmation_contract
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0

Methodology v1:
- Each upstream signal is normalized evidence in [-1.0, 1.0].
- Every signal has equal weight; signal names do not affect the result.
- The confirmation score is the arithmetic mean of all supplied signals.
- Confirmation is true when the absolute score reaches the deterministic threshold of 0.5.
- Empty input, non-finite values, and values outside [-1.0, 1.0] are invalid.
- No market, provider, timeframe, execution, cost, liquidity, risk, or decision semantics are embedded here.
"""

from math import isfinite

from composition.confirmation_contract import (
    CONFIRMATION_CONTRACT_ID,
    CONFIRMATION_CONTRACT_VERSION,
    ConfirmationOutput,
    ConfirmationRequest,
)

CONFIRMATION_METHODOLOGY_ID = "deterministic_threshold_confirmation_v1"
CONFIRMATION_METHODOLOGY_VERSION = "1.0.0"
CONFIRMATION_THRESHOLD = 0.5


class DeterministicThresholdConfirmation:
    """Confirm normalized evidence when its equal-weight mean reaches ±0.5."""

    contract_id = CONFIRMATION_CONTRACT_ID
    contract_version = CONFIRMATION_CONTRACT_VERSION
    confirmation_id = CONFIRMATION_METHODOLOGY_ID

    def confirm(self, request: ConfirmationRequest) -> ConfirmationOutput:
        if not request.signals:
            raise ValueError("signals must not be empty")

        values = tuple(request.signals.values())
        if any(not isfinite(value) for value in values):
            raise ValueError("signals must contain only finite values")
        if any(not -1.0 <= value <= 1.0 for value in values):
            raise ValueError("signals must be within [-1.0, 1.0]")

        score = sum(values) / len(values)
        return ConfirmationOutput(
            confirmed=abs(score) >= CONFIRMATION_THRESHOLD,
            score=score,
            event_time=request.event_time,
            confirmation_id=self.confirmation_id,
        )
