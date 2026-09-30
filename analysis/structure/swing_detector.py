"""FILE: analysis/structure/swing_detector.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-01
DATE_PERSIAN: 1405-07-09
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Detect deterministic confirmed market-structure swing highs and lows without look-ahead.
LAYER: analysis
OWNS: Confirmed swing detection methodology and immutable swing observations.
DOES_NOT_OWN: structural labeling, trading decisions, risk, execution, provider I/O.
DEPENDENCIES: dataclasses, typing, shared.contracts.market_structure
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from shared.contracts.market_structure import MARKET_STRUCTURE_METHODOLOGY, MarketStructureBar

SwingKind = Literal["high", "low"]

@dataclass(frozen=True, slots=True)
class ConfirmedSwing:
    """A pivot that has completed its configured right-side confirmation window."""

    kind: SwingKind
    index: int
    bar: MarketStructureBar

class DeterministicSwingDetector:
    """Detect strict confirmed pivots without look-ahead."""

    def __init__(self) -> None:
        self._methodology = MARKET_STRUCTURE_METHODOLOGY

    def detect(self, bars: tuple[MarketStructureBar, ...]) -> tuple[ConfirmedSwing, ...]:
        left = self._methodology.pivot_left_bars
        right = self._methodology.pivot_right_bars
        if len(bars) < left + right + 1:
            raise ValueError("insufficient history for deterministic swing detection")

        swings: list[ConfirmedSwing] = []
        for index in range(left, len(bars) - right):
            candidate = bars[index]
            neighbours = (*bars[index - left : index], *bars[index + 1 : index + right + 1])
            if all(candidate.high > neighbour.high for neighbour in neighbours):
                swings.append(ConfirmedSwing("high", index, candidate))
            if all(candidate.low < neighbour.low for neighbour in neighbours):
                swings.append(ConfirmedSwing("low", index, candidate))
        return tuple(sorted(swings, key=lambda swing: (swing.index, swing.kind)))

