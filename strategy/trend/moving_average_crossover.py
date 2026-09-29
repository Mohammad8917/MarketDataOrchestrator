"""FILE: strategy/trend/moving_average_crossover.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-29
DATE_PERSIAN: 1405-07-07
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Generate deterministic moving-average crossover trend positions from historical market bars.
LAYER: strategy
OWNS: Fast/slow period validation, rolling close averages, and position transitions.
DOES_NOT_OWN: backtest execution, portfolio accounting, persistence, provider I/O, or performance metrics.
DEPENDENCIES: dataclasses, enum, shared.contracts.market_bar
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from shared.contracts.market_bar import MarketBar


class MovingAverageCrossoverPosition(Enum):
    """Moving-average crossover position state."""

    FLAT = 0
    LONG = 1


@dataclass(frozen=True, slots=True)
class MovingAverageCrossoverStrategy:
    """Close-confirmed fast/slow moving-average trend strategy."""

    fast_period: int = 10
    slow_period: int = 30

    def __post_init__(self) -> None:
        if (
            not isinstance(self.fast_period, int)
            or isinstance(self.fast_period, bool)
            or self.fast_period <= 0
        ):
            raise ValueError("fast period must be positive")
        if (
            not isinstance(self.slow_period, int)
            or isinstance(self.slow_period, bool)
            or self.slow_period <= 0
        ):
            raise ValueError("slow period must be positive")
        if self.fast_period >= self.slow_period:
            raise ValueError("fast period must be less than slow period")

    def signals(
        self,
        events: tuple[MarketBar, ...],
    ) -> tuple[MovingAverageCrossoverPosition, ...]:
        if any(
            current.event_time <= previous.event_time
            for previous, current in zip(events, events[1:])
        ):
            raise ValueError("events must be strictly ordered by event_time")

        positions: list[MovingAverageCrossoverPosition] = []
        for index in range(len(events)):
            if index + 1 < self.slow_period:
                positions.append(MovingAverageCrossoverPosition.FLAT)
                continue

            fast_window = events[index + 1 - self.fast_period : index + 1]
            slow_window = events[index + 1 - self.slow_period : index + 1]
            fast_average = sum(bar.close for bar in fast_window) / self.fast_period
            slow_average = sum(bar.close for bar in slow_window) / self.slow_period

            positions.append(
                MovingAverageCrossoverPosition.LONG
                if fast_average > slow_average
                else MovingAverageCrossoverPosition.FLAT
            )

        return tuple(positions)
