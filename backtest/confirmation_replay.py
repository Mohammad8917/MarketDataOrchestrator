"""FILE: backtest/confirmation_replay.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-01
DATE_PERSIAN: 1405-07-09
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Replay analytical signal confirmation point-in-time for historical requests.
LAYER: backtest
OWNS: Confirmation replay ordering and output collection.
DOES_NOT_OWN: confirmation methodology, market-data I/O, persistence, cost, risk, decision finalization, trading actions
DEPENDENCIES: composition.confirmation_contract
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from dataclasses import dataclass

from composition.confirmation_contract import (
    ConfirmationOutput,
    ConfirmationRequest,
    SignalConfirmation,
)

CONTRACT_ID = "backtest_confirmation_replay_boundary"
CONTRACT_VERSION = "1.0.0"


@dataclass(frozen=True, slots=True)
class ConfirmationReplayOutput:
    results: tuple[ConfirmationOutput, ...]
    contract_version: str = CONTRACT_VERSION


class ConfirmationReplay:
    """Replay confirmation methodology without future request observations."""

    contract_id = CONTRACT_ID
    contract_version = CONTRACT_VERSION

    @staticmethod
    def _validate_requests(requests: tuple[ConfirmationRequest, ...]) -> None:
        if not requests:
            raise ValueError("requests must not be empty")
        if any(
            current.event_time <= previous.event_time
            for previous, current in zip(requests, requests[1:])
        ):
            raise ValueError("requests must be strictly ordered by event_time")

    @staticmethod
    def _validate_output(
        request: ConfirmationRequest,
        output: ConfirmationOutput,
    ) -> None:
        if output.event_time != request.event_time:
            raise ValueError("confirmation output event_time must match request")

    def run(
        self,
        requests: tuple[ConfirmationRequest, ...],
        confirmer: SignalConfirmation,
    ) -> ConfirmationReplayOutput:
        self._validate_requests(requests)
        if not isinstance(confirmer, SignalConfirmation):
            raise TypeError("confirmer must implement SignalConfirmation")

        results: list[ConfirmationOutput] = []
        for request in requests:
            output = confirmer.confirm(request)
            self._validate_output(request, output)
            results.append(output)

        return ConfirmationReplayOutput(results=tuple(results))
