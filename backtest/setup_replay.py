"""FILE: backtest/setup_replay.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Replay deterministic setup evaluation point-in-time for historical requests.
LAYER: backtest
OWNS: Setup replay ordering, evaluator delegation, and immutable output collection.
DOES_NOT_OWN: setup methodology, market-data I/O, persistence, cost, liquidity, risk, decision finalization, trading actions
DEPENDENCIES: shared.interfaces.setup
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from dataclasses import dataclass

from shared.interfaces.setup import Setup, SetupOutput, SetupRequest

CONTRACT_ID = "backtest_setup_replay_boundary"
CONTRACT_VERSION = "1.0.0"


@dataclass(frozen=True, slots=True)
class SetupReplayOutput:
    results: tuple[SetupOutput, ...]
    contract_version: str = CONTRACT_VERSION


class SetupReplay:
    """Replay setup methodology without future observations."""

    contract_id = CONTRACT_ID
    contract_version = CONTRACT_VERSION

    @staticmethod
    def _validate_requests(
        requests: object,
    ) -> tuple[SetupRequest, ...]:
        if not isinstance(requests, tuple):
            raise ValueError("requests must be a tuple")
        if any(not isinstance(request, SetupRequest) for request in requests):
            raise ValueError("requests must contain only SetupRequest values")
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
        request: SetupRequest,
        output: object,
    ) -> SetupOutput:
        if not isinstance(output, SetupOutput):
            raise TypeError("setup must return SetupOutput")
        if output.event_time != request.event_time:
            raise ValueError("setup output event_time must match request")
        return output

    def run(
        self,
        requests: tuple[SetupRequest, ...],
        setup: Setup,
    ) -> SetupReplayOutput:
        validated_requests = self._validate_requests(requests)
        if not isinstance(setup, Setup):
            raise TypeError("setup must implement Setup")

        results: list[SetupOutput] = []
        for request in validated_requests:
            output = self._validate_output(request, setup.evaluate(request))
            results.append(output)

        return SetupReplayOutput(results=tuple(results))
