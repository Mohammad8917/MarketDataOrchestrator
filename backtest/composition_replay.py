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
    def _validate_requests(
        requests: object,
    ) -> tuple[CompositionRequest, ...]:
        if not isinstance(requests, tuple):
            raise ValueError("requests must be a tuple")
        if any(not isinstance(request, CompositionRequest) for request in requests):
            raise ValueError(
                "requests must contain only CompositionRequest values"
            )
        if not requests:
            raise ValueError("requests must not be empty")
        if any(
            current.event_time <= previous.event_time
            for previous, current in zip(requests, requests[1:])
        ):
            raise ValueError("requests must be strictly ordered by event_time")
        return requests

    @staticmethod
    def _validate_output(
        request: CompositionRequest,
        output: object,
    ) -> CompositionOutput:
        if not isinstance(output, CompositionOutput):
            raise TypeError("composer must return CompositionOutput")
        if output.event_time != request.event_time:
            raise ValueError("composition output event_time must match request")

    def run(
        self,
        requests: tuple[CompositionRequest, ...],
        composer: SignalComposer,
    ) -> CompositionReplayOutput:
        validated_requests = self._validate_requests(requests)
        if not isinstance(composer, SignalComposer):
            raise TypeError("composer must implement SignalComposer")

        results: list[CompositionOutput] = []
        for request in validated_requests:
            output = self._validate_output(request, composer.compose(request))
            results.append(output)

        return CompositionReplayOutput(results=tuple(results))
