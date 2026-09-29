""FILE: strategy/volatility/bollinger_mean_reversion.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-29
DATE_PERSIAN: 1405-07-07
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Generate deterministic Bollinger-band mean-reversion positions from historical market bars.
LAYER: strategy
OWNS: Bollinger period/deviation validation, rolling bands, and position transitions.
DOES_NOT_OWN: backtest execution, portfolio accounting, persistence, provider I/O, or performance metrics.
DEPENDENCIES: dataclasses, decimal, enum, shared.contracts.market_bar
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

from shared.contracts.market_bar import MarketBar


class BollingerMeanReversionPosition(Enum):
    """Bollinger-band mean-reversion position state."""

    FLAT = 0
    LONG = 1


@dataclass(frozen=True, slots=True)
class BollingerMeanReversionStrategy:
    """Close-confirmed Bollinger-band mean-reversion strategy."""

    period: int = 20
    deviation_multiplier: Decimal = Decimal("2")

    def __post_init__(self) -> None:
        if not isinstance(self.period, int) or isinstance(self.period, bool) or self.period <= 1:
            raise ValueError("period must be greater than 1")
        if (
            not isinstance(self.deviation_multiplier, Decimal)
            or not self.deviation_multiplier.is_finite()
            or self.deviation_multiplier <= 0
        ):
            raise ValueError("deviation multiplier must be a positive finite Decimal")

    def signals(
        self,
        events: tuple[MarketBar, ...],
    ) -> tuple[BollingerMeanReversionPosition, ...]:
        if any(
            current.event_time <= previous.event_time
            for previous, current in zip(events, events[1:])
        ):
            raise ValueError("events must be strictly ordered by event_time")

        positions: list[BollingerMeanReversionPosition] = []
        position = BollingerMeanReversionPosition.FLAT

        for index in range(len(events)):
            if index + 1 < self.period:
                positions.append(position)
                continue

            window = events[index + 1 - self.period : index + 1]
            mean = sum((bar.close for bar in window), Decimal("0")) / self.period
            variance = (
                sum(
                    ((bar.close - mean) ** 2 for bar in window),
                    Decimal("0"),
                )
                / self.period
            )
            standard_deviation = variance.sqrt()
            lower_band = mean - (self.deviation_multiplier * standard_deviation)

            if (
                position is BollingerMeanReversionPosition.FLAT
                and events[index].close <= lower_band
            ):
                position = BollingerMeanReversionPosition.LONG
            elif position is BollingerMeanReversionPosition.LONG and events[index].close >= mean:
                position = BollingerMeanReversionPosition.FLAT

            positions.append(position)

        return tuple(positions)
"