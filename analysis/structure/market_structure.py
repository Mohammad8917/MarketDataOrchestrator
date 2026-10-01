"""FILE: analysis/structure/market_structure.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-01
DATE_PERSIAN: 1405-07-09
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Compose deterministic confirmed swings, structural labels, and descriptive break events into the market-structure contract output.
LAYER: analysis
OWNS: Market-structure evaluation orchestration at the analysis boundary.
DOES_NOT_OWN: structure methodology definition, trading decisions, risk, execution, provider I/O, persistence.
DEPENDENCIES: analysis.structure.break_detector; analysis.structure.swing_detector; analysis.structure.swing_labeler; shared.contracts.market_structure
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from analysis.structure.break_detector import DeterministicStructureBreakDetector
from analysis.structure.swing_detector import DeterministicSwingDetector
from analysis.structure.swing_labeler import DeterministicStructureLabeler
from shared.contracts.market_structure import (
    MARKET_STRUCTURE_CONTRACT_ID,
    MARKET_STRUCTURE_CONTRACT_VERSION,
    MarketStructureEvaluator,
    MarketStructureOutput,
    MarketStructureRequest,
)


class DeterministicMarketStructureEvaluator:
    """Evaluate the implemented deterministic structural observations.

    The evaluator composes only already-defined methodology components. The
    optional output state remains None until a separately versioned state
    classification methodology is specified; no implicit classification rule
    is invented at this boundary.
    """

    contract_id = MARKET_STRUCTURE_CONTRACT_ID
    contract_version = MARKET_STRUCTURE_CONTRACT_VERSION

    def __init__(
        self,
        swing_detector: DeterministicSwingDetector | None = None,
        labeler: DeterministicStructureLabeler | None = None,
        break_detector: DeterministicStructureBreakDetector | None = None,
    ) -> None:
        self._swing_detector = swing_detector or DeterministicSwingDetector()
        self._labeler = labeler or DeterministicStructureLabeler()
        self._break_detector = break_detector or DeterministicStructureBreakDetector()

    def evaluate(self, request: MarketStructureRequest) -> MarketStructureOutput:
        swings = self._swing_detector.detect(request.bars)
        points = self._labeler.label(swings)
        events = self._break_detector.detect(request.bars, swings)

        return MarketStructureOutput(
            points=points,
            events=events,
            state=None,
            event_time=request.event_time,
            source_event_id=request.source_event_id,
        )


MARKET_STRUCTURE_EVALUATOR: type[MarketStructureEvaluator] = (
    DeterministicMarketStructureEvaluator
)
