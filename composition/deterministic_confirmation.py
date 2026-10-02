"""FILE: composition/deterministic_confirmation.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Produce deterministic directional confirmation from normalized signal directions.
LAYER: composition
OWNS: directional-majority confirmation methodology and deterministic confirmation identity.
DOES_NOT_OWN: signal generation, market-data I/O, persistence, cost, liquidity, risk, decision finalization, or trading execution.
DEPENDENCIES: hashlib, composition.confirmation_contract
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from composition.confirmation_contract import (
    CONFIRMATION_CONTRACT_ID,
    CONFIRMATION_CONTRACT_VERSION,
    ConfirmationOutput,
    ConfirmationRequest,
)


@dataclass(frozen=True, slots=True)
class DeterministicMajorityConfirmation:
    """Confirm when at least a configurable directional majority agrees."""

    minimum_agreement: float = 0.5
    minimum_active_signals: int = 2
    contract_id: str = CONFIRMATION_CONTRACT_ID
    contract_version: str = CONFIRMATION_CONTRACT_VERSION
    confirmation_id: str = "deterministic-majority"

    def __post_init__(self) -> None:
        if not 0.0 < self.minimum_agreement <= 1.0:
            raise ValueError("minimum_agreement must be within (0, 1]")
        if self.minimum_active_signals < 2:
            raise ValueError("minimum_active_signals must be at least 2")

    def confirm(self, request: ConfirmationRequest) -> ConfirmationOutput:
        active = tuple(value for value in request.signals.values() if value != 0.0)
        if len(active) < self.minimum_active_signals:
            score = 0.0
            confirmed = False
        else:
            positive = sum(value > 0.0 for value in active)
            negative = sum(value < 0.0 for value in active)
            if positive > negative:
                score = positive / len(active)
            elif negative > positive:
                score = -negative / len(active)
            else:
                score = 0.0
            confirmed = abs(score) >= self.minimum_agreement

        identity = "|".join(
            (
                self.contract_id,
                self.contract_version,
                request.source_event_id,
                request.event_time.isoformat(),
                *(f"{name}={request.signals[name]:.12g}" for name in sorted(request.signals)),
            )
        ).encode("utf-8")

        return ConfirmationOutput(
            confirmed=confirmed,
            score=score,
            event_time=request.event_time,
            confirmation_id=sha256(identity).hexdigest(),
        )
