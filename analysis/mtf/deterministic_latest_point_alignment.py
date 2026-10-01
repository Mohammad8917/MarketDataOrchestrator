"""Deterministic latest-point multi-timeframe structure methodology."""

from __future__ import annotations

from shared.contracts.mtf_structure import (
    MTF_STRUCTURE_CONTRACT_ID,
    MTF_STRUCTURE_CONTRACT_VERSION,
    MtfStructureEvaluator,
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
    def _direction(points) -> str:
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
    def _alignment(directions: tuple[str, ...]) -> str:
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
