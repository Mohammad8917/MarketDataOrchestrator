"""FILE: backtest/composition_replay.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-01
DATE_PERSIAN: 1405-07-09
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Replay analytical signal composition point-in-time for historical requests.
LAYER: backtest
OWNS: Composition replay ordering and output collection.
DOES_NOT_OWN: composition methodology, market-data I/O, persistence, confirmation, cost, risk, decision finalization, trading actions
DEPENDENCIES: composition.composer
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from dataclasses import dataclass

from composition.composer import CompositionOutput, CompositionRequest, SignalComposer

CONTRACT_ID = "backtest_composition_replay_boundary"
CONTRACT_VERSION = "1.0.0"


@dataclass(frozen=True, slots=True)
class CompositionReplayOutput:
    results: tuple[CompositionOutput, ...]
    contract_version: str = CONTRACT_VERSION


class CompositionReplay:
    """Replay composition methodology without future observations."""

    contract_id = CONTRACT_ID
    contract_version = CONTRACT_VERSION

    @staticmethod
    def _validate_requests(requests: tuple[CompositionRequest, ...]) -> None:
        if not requests:
            raise ValueError("requests must not be empty")
        if any(
            current.event_time <= previous.event_time
            for previous, current in zip(requests, requests[1:])
        ):
            raise ValueError("requests must be strictly ordered by event_time")

    @staticmethod
    def _validate_output(
        request: CompositionRequest,
        output: CompositionOutput,
    ) -> None:
        if output.event_time != request.event_time:
            raise ValueError("composition output event_time must match request")

    def run(
        self,
        requests: tuple[CompositionRequest, ...],
        composer: SignalComposer,
    ) -> CompositionReplayOutput:
        self._validate_requests(requests)
        if not isinstance(composer, SignalComposer):
            raise TypeError("composer must implement SignalComposer")

        results: list[CompositionOutput] = []
        for request in requests:
            output = composer.compose(request)
            self._validate_output(request, output)
            results.append(output)

        return CompositionReplayOutput(results=tuple(results))
