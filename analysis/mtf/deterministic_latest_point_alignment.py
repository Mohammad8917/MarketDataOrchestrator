"""FILE: analysis/mtf/deterministic_latest_point_alignment.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-01
DATE_PERSIAN: 1405-07-09
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Implement deterministic latest-confirmed-point directional alignment across named timeframes.
LAYER: analysis
OWNS: Multi-timeframe structural direction derivation and alignment methodology only.
DOES_NOT_OWN: swing detection, market-data I/O, persistence, cost, risk, decision finalization, trading actions.
DEPENDENCIES: shared.contracts.mtf_structure
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from shared.contracts.market_structure import StructurePoint

from shared.contracts.mtf_structure import (
    MTF_STRUCTURE_CONTRACT_ID,
    MTF_STRUCTURE_CONTRACT_VERSION,
    MtfStructureEvaluator,
    StructureAlignment,
    StructureDirection,
    MtfStructureObservation,
    MtfStructureOutput,
    MtfStructureRequest,
)

METHODOLOGY_ID = "deterministic_latest_point_alignment"
METHODOLOGY_VERSION = "1.0.0"


class DeterministicLatestPointAlignment:
    contract_id = MTF_STRUCTURE_CONTRACT_ID
    contract_version = MTF_STRUCTURE_CONTRACT_VERSION
    methodology_id = METHODOLOGY_ID
    methodology_version = METHODOLOGY_VERSION

    @staticmethod
    def _direction(points: tuple[StructurePoint, ...]) -> StructureDirection:
        if not points:
            return "unknown"
        latest_time = max(point.event_time for point in points)
        kinds = {point.kind for point in points if point.event_time == latest_time}
        if kinds <= {"HH", "HL"}:
            return "bullish"
        if kinds <= {"LH", "LL"}:
            return "bearish"
        return "unknown"

    @staticmethod
    def _alignment(directions: tuple[StructureDirection, ...]) -> StructureAlignment:
        known = {direction for direction in directions if direction != "unknown"}
        if not known:
            return "insufficient"
        if known == {"bullish"}:
            return "bullish"
        if known == {"bearish"}:
            return "bearish"
        return "mixed"

    def evaluate(self, request: MtfStructureRequest) -> MtfStructureOutput:
        observations = tuple(
            MtfStructureObservation(
                item.timeframe,
                self._direction(item.structure.points),
            )
            for item in request.inputs
        )
        return MtfStructureOutput(
            observations,
            self._alignment(tuple(item.direction for item in observations)),
            request.event_time,
            request.source_event_id,
        )


MTF_STRUCTURE_EVALUATOR: type[MtfStructureEvaluator] = DeterministicLatestPointAlignment
