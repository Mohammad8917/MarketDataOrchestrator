"""Deterministic confirmed market-structure swing detection."""

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
            neighbours = (*bars[index - left:index], *bars[index + 1:index + right + 1])
            if all(candidate.high > neighbour.high for neighbour in neighbours):
                swings.append(ConfirmedSwing("high", index, candidate))
            if all(candidate.low < neighbour.low for neighbour in neighbours):
                swings.append(ConfirmedSwing("low", index, candidate))
        return tuple(sorted(swings, key=lambda swing: (swing.index, swing.kind)))
