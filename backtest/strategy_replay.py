"""FILE: backtest/strategy_replay.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-10-03
DATE_PERSIAN: 1405-07-11
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Replay canonical strategy evaluations point-in-time over historical requests.
LAYER: backtest
OWNS: Strategy replay ordering, delegation, output alignment, and immutable output collection.
DOES_NOT_OWN: strategy methodology, portfolio accounting, performance metrics, cost, liquidity, risk, decision finalization, trading execution
DEPENDENCIES: shared.interfaces.strategy
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from dataclasses import dataclass

from shared.interfaces.strategy import Strategy, StrategyOutput, StrategyRequest

CONTRACT_ID = "backtest_strategy_replay_boundary"
CONTRACT_VERSION = "1.0.0"


@dataclass(frozen=True, slots=True)
class StrategyReplayOutput:
    """Immutable ordered strategy observations produced by replay."""

    results: tuple[StrategyOutput, ...]
    contract_version: str = CONTRACT_VERSION


class StrategyReplay:
    """Replay a canonical Strategy without introducing trading semantics."""

    contract_id = CONTRACT_ID
    contract_version = CONTRACT_VERSION

    @staticmethod
    def _validate_requests(requests: object) -> tuple[StrategyRequest, ...]:
        if not isinstance(requests, tuple):
            raise ValueError("requests must be a tuple")
        if not all(isinstance(request, StrategyRequest) for request in requests):
            raise ValueError("requests must contain only StrategyRequest values")
        if not requests:
            raise ValueError("requests must not be empty")
        if any(
            current.event_time <= previous.event_time
            for previous, current in zip(requests, requests[1:])
        ):
            raise ValueError("requests must be strictly ordered by event_time")
        return requests

    @staticmethod
    def _validate_output(request: StrategyRequest, output: object) -> None:
        if not isinstance(output, StrategyOutput):
            raise TypeError("strategy must return StrategyOutput")
        if output.event_time != request.event_time:
            raise ValueError("strategy output event_time must match request")

    def run(
        self,
        requests: tuple[StrategyRequest, ...],
        strategy: Strategy,
    ) -> StrategyReplayOutput:
        validated_requests = self._validate_requests(requests)
        if not isinstance(strategy, Strategy):
            raise TypeError("strategy must implement Strategy")

        results: list[StrategyOutput] = []
        for request in validated_requests:
            output = strategy.evaluate(request)
            self._validate_output(request, output)
            results.append(output)

        return StrategyReplayOutput(results=tuple(results))
