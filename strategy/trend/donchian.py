"""FILE: strategy/trend/donchian.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-29
DATE_PERSIAN: 1405-07-07
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Generate deterministic Donchian trend positions from historical market bars.
LAYER: strategy
OWNS: Donchian period validation, prior-channel calculation, and position transitions.
DOES_NOT_OWN: backtest execution, portfolio accounting, persistence, provider I/O, or performance metrics.
DEPENDENCIES: shared.contracts.market_bar
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from backtest.strategy import BacktestPosition
from shared.contracts.market_bar import MarketBar


class DonchianPosition(Enum):
    """Public Donchian position state."""

    FLAT = 0
    LONG = 1


@dataclass(frozen=True, slots=True)
class DonchianStrategy:
    """Close-confirmed Donchian strategy using only prior bars."""

    period: int = 20

    def __post_init__(self) -> None:
        if self.period < 2:
            raise ValueError("period must be at least 2")

    def signals(self, events: tuple[MarketBar, ...]) -> tuple[BacktestPosition, ...]:
        if any(
            current.event_time <= previous.event_time
            for previous, current in zip(events, events[1:])
        ):
            raise ValueError("events must be strictly ordered by event_time")

        positions: list[BacktestPosition] = []
        position = BacktestPosition.FLAT

        for index, event in enumerate(events):
            if index < self.period:
                positions.append(position)
                continue

            window = events[index - self.period : index]
            upper = max(bar.high for bar in window)
            lower = min(bar.low for bar in window)

            if position is BacktestPosition.FLAT and event.close > upper:
                position = BacktestPosition.LONG
            elif position is BacktestPosition.LONG and event.close < lower:
                position = BacktestPosition.FLAT

            positions.append(position)

        return tuple(positions)


def public_position(position: BacktestPosition) -> DonchianPosition:
    """Map the execution-neutral position to the Donchian public position type."""
    return DonchianPosition(position.value)
