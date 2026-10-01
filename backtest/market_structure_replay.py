"""FILE: backtest/market_structure_replay.py
KIT: Architecture & Implementation Compliance Kit
RESPONSIBILITY: Replay deterministic market-structure analysis point-in-time for historical requests.
LAYER: backtest
OWNS: Market-structure replay ordering, evaluator delegation, and immutable output collection.
DOES_NOT_OWN: structure methodology, market-data I/O, persistence, cost, risk, decision finalization, trading actions
DEPENDENCIES: shared.contracts.market_structure
PYTHON: >=3.13
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
    def _validate_requests(requests: tuple[MarketStructureRequest, ...]) -> None:
        if not requests:
            raise ValueError("requests must not be empty")
        if any(
            current.event_time <= previous.event_time
            for previous, current in zip(requests, requests[1:])
        ):
            raise ValueError("requests must be strictly ordered by event_time")

    @staticmethod
    def _validate_output(request: MarketStructureRequest, output: MarketStructureOutput) -> None:
        if output.event_time != request.event_time:
            raise ValueError("market structure output event_time must match request")
        if output.source_event_id != request.source_event_id:
            raise ValueError("market structure output source_event_id must match request")

    def run(
        self,
        requests: tuple[MarketStructureRequest, ...],
        evaluator: MarketStructureEvaluator,
    ) -> MarketStructureReplayOutput:
        self._validate_requests(requests)
        if not isinstance(evaluator, MarketStructureEvaluator):
            raise TypeError("evaluator must implement MarketStructureEvaluator")

        results: list[MarketStructureOutput] = []
        for request in requests:
            output = evaluator.evaluate(request)
            self._validate_output(request, output)
            results.append(output)

        return MarketStructureReplayOutput(results=tuple(results))