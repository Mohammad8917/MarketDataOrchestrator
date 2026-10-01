"""FILE: backtest/mtf_structure_replay.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Replay deterministic multi-timeframe structure alignment point-in-time.
LAYER: backtest
OWNS: MTF replay ordering, evaluator delegation, and immutable output collection.
DOES_NOT_OWN: structure methodology, market-data I/O, persistence, cost, risk, decision finalization, trading actions
DEPENDENCIES: shared.contracts.mtf_structure
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from dataclasses import dataclass

from shared.contracts.mtf_structure import (
    MtfStructureEvaluator,
    MtfStructureOutput,
    MtfStructureRequest,
)

CONTRACT_ID = "backtest_mtf_structure_replay_boundary"
CONTRACT_VERSION = "1.0.0"


@dataclass(frozen=True, slots=True)
class MtfStructureReplayOutput:
    results: tuple[MtfStructureOutput, ...]
    contract_version: str = CONTRACT_VERSION


class MtfStructureReplay:
    """Replay MTF structure without future observations or side effects."""

    contract_id = CONTRACT_ID
    contract_version = CONTRACT_VERSION

    @staticmethod
    def _validate_requests(requests: tuple[MtfStructureRequest, ...]) -> None:
        if not requests:
            raise ValueError("requests must not be empty")
        if any(
            current.event_time <= previous.event_time
            for previous, current in zip(requests, requests[1:])
        ):
            raise ValueError("requests must be strictly ordered by event_time")

    @staticmethod
    def _validate_output(
        request: MtfStructureRequest,
        output: MtfStructureOutput,
    ) -> None:
        if output.event_time != request.event_time:
            raise ValueError("MTF structure output event_time must match request")
        if output.source_event_id != request.source_event_id:
            raise ValueError("MTF structure output source_event_id must match request")

    def run(
        self,
        requests: tuple[MtfStructureRequest, ...],
        evaluator: MtfStructureEvaluator,
    ) -> MtfStructureReplayOutput:
        self._validate_requests(requests)
        if not isinstance(evaluator, MtfStructureEvaluator):
            raise TypeError("evaluator must implement MtfStructureEvaluator")

        results: list[MtfStructureOutput] = []
        for request in requests:
            output = evaluator.evaluate(request)
            self._validate_output(request, output)
            results.append(output)

        return MtfStructureReplayOutput(results=tuple(results))
