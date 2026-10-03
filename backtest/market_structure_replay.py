"""FILE: backtest/market_structure_replay.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-10-03
DATE_PERSIAN: 1405-07-11
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Replay deterministic market-structure analysis point-in-time for historical requests.
LAYER: backtest
OWNS: Market-structure replay ordering, evaluator delegation, and immutable output collection.
DOES_NOT_OWN: structure methodology, market-data I/O, persistence, cost, risk, decision finalization, trading actions
DEPENDENCIES: shared.contracts.market_structure
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from dataclasses import dataclass

from shared.contracts.market_structure import (
    MarketStructureEvaluator,
    MarketStructureOutput,
    MarketStructureRequest,
)

CONTRACT_ID = "backtest_market_structure_replay_boundary"
CONTRACT_VERSION = "1.0.0"


@dataclass(frozen=True, slots=True)
class MarketStructureReplayOutput:
    results: tuple[MarketStructureOutput, ...]
    contract_version: str = CONTRACT_VERSION


class MarketStructureReplay:
    """Replay market structure without future observations."""

    contract_id = CONTRACT_ID
    contract_version = CONTRACT_VERSION

    @staticmethod
    def _validate_requests(requests: object) -> tuple[MarketStructureRequest, ...]:
        if not isinstance(requests, tuple):
            raise ValueError("requests must be a tuple")
        if not all(isinstance(request, MarketStructureRequest) for request in requests):
            raise ValueError("requests must contain only MarketStructureRequest values")
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
        request: MarketStructureRequest,
        output: object,
    ) -> None:
        if not isinstance(output, MarketStructureOutput):
            raise TypeError("evaluator must return MarketStructureOutput")
        if output.event_time != request.event_time:
            raise ValueError("market structure output event_time must match request")
        if output.source_event_id != request.source_event_id:
            raise ValueError("market structure output source_event_id must match request")

    def run(
        self,
        requests: tuple[MarketStructureRequest, ...],
        evaluator: MarketStructureEvaluator,
    ) -> MarketStructureReplayOutput:
        validated_requests = self._validate_requests(requests)
        if not isinstance(evaluator, MarketStructureEvaluator):
            raise TypeError("evaluator must implement MarketStructureEvaluator")

        results: list[MarketStructureOutput] = []
        for request in validated_requests:
            output = evaluator.evaluate(request)
            self._validate_output(request, output)
            results.append(output)

        return MarketStructureReplayOutput(results=tuple(results))
