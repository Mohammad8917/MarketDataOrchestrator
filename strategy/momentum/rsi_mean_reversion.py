"""FILE: strategy/momentum/rsi_mean_reversion.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-29
DATE_PERSIAN: 1405-07-07
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Generate deterministic RSI mean-reversion positions from historical market bars.
LAYER: strategy
OWNS: RSI period/threshold validation, Wilder RSI calculation, and position transitions.
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


class RsiMeanReversionPosition(Enum):
    """RSI mean-reversion position state."""

    FLAT = 0
    LONG = 1


@dataclass(frozen=True, slots=True)
class RsiMeanReversionStrategy:
    """Wilder-RSI mean-reversion strategy using close-confirmed signals."""

    period: int = 14
    oversold: Decimal = Decimal("30")
    overbought: Decimal = Decimal("70")

    def __post_init__(self) -> None:
        if not isinstance(self.period, int) or isinstance(self.period, bool) or self.period <= 0:
            raise ValueError("period must be positive")
        if not isinstance(self.oversold, Decimal) or not self.oversold.is_finite():
            raise ValueError("oversold must be a finite Decimal")
        if not isinstance(self.overbought, Decimal) or not self.overbought.is_finite():
            raise ValueError("overbought must be a finite Decimal")
        if self.oversold < Decimal("0") or self.oversold > Decimal("100"):
            raise ValueError("oversold must be between 0 and 100")
        if self.overbought < Decimal("0") or self.overbought > Decimal("100"):
            raise ValueError("overbought must be between 0 and 100")
        if self.oversold >= self.overbought:
            raise ValueError("oversold must be less than overbought")

    @staticmethod
    def _validate_events(events: tuple[MarketBar, ...]) -> None:
        if any(
            current.event_time <= previous.event_time
            for previous, current in zip(events, events[1:])
        ):
            raise ValueError("events must be strictly ordered by event_time")

    def _initial_averages(
        self,
        events: tuple[MarketBar, ...],
    ) -> tuple[Decimal, Decimal]:
        gains = [
            max(events[i].close - events[i - 1].close, Decimal("0"))
            for i in range(1, self.period + 1)
        ]
        losses = [
            max(events[i - 1].close - events[i].close, Decimal("0"))
            for i in range(1, self.period + 1)
        ]
        return (
            sum(gains, Decimal("0")) / self.period,
            sum(losses, Decimal("0")) / self.period,
        )

    def _updated_averages(
        self,
        average_gain: Decimal,
        average_loss: Decimal,
        gain: Decimal,
        loss: Decimal,
    ) -> tuple[Decimal, Decimal]:
        return (
            ((average_gain * (self.period - 1)) + gain) / self.period,
            ((average_loss * (self.period - 1)) + loss) / self.period,
        )

    @staticmethod
    def _rsi(average_gain: Decimal, average_loss: Decimal) -> Decimal:
        if average_loss == 0:
            return Decimal("100") if average_gain > 0 else Decimal("50")
        relative_strength = average_gain / average_loss
        return Decimal("100") - (Decimal("100") / (Decimal("1") + relative_strength))

    def _position_from_rsi(
        self,
        rsi: Decimal,
        position: RsiMeanReversionPosition,
    ) -> RsiMeanReversionPosition:
        if rsi <= self.oversold:
            return RsiMeanReversionPosition.LONG
        if rsi >= self.overbought:
            return RsiMeanReversionPosition.FLAT
        return position

    def signals(
        self,
        events: tuple[MarketBar, ...],
    ) -> tuple[RsiMeanReversionPosition, ...]:
        self._validate_events(events)
        positions: list[RsiMeanReversionPosition] = []
        position = RsiMeanReversionPosition.FLAT
        average_gain: Decimal | None = None
        average_loss: Decimal | None = None

        for index, event in enumerate(events):
            if index == 0:
                positions.append(position)
                continue

            change = event.close - events[index - 1].close
            gain = max(change, Decimal("0"))
            loss = max(-change, Decimal("0"))

            if index < self.period:
                positions.append(position)
                continue

            if index == self.period:
                average_gain, average_loss = self._initial_averages(events)
            else:
                if average_gain is None or average_loss is None:
                    raise RuntimeError("RSI averages were not initialized")
                average_gain, average_loss = self._updated_averages(
                    average_gain, average_loss, gain, loss
                )

            rsi = self._rsi(average_gain, average_loss)
            position = self._position_from_rsi(rsi, position)
            positions.append(position)

        return tuple(positions)
