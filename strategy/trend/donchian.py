"""Close-confirmed Donchian trend-following strategy."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from shared.contracts.market_bar import MarketBar


class DonchianPosition(Enum):
    """Long/flat position emitted by the strategy."""

    FLAT = 0
    LONG = 1


@dataclass(frozen=True, slots=True)
class DonchianStrategy:
    """Generate signals from the previous period candles only."""

    period: int = 20

    def __post_init__(self) -> None:
        if self.period < 2:
            raise ValueError("period must be at least 2")

    def signals(self, events: tuple[MarketBar, ...]) -> tuple[DonchianPosition, ...]:
        """Return one position signal per candle without lookahead."""
        if any(
            events[index].event_time >= events[index + 1].event_time
            for index in range(len(events) - 1)
        ):
            raise ValueError("events must be strictly ordered by event_time")

        positions: list[DonchianPosition] = [DonchianPosition.FLAT] * len(events)
        position = DonchianPosition.FLAT

        for index in range(self.period, len(events)):
            window = events[index - self.period : index]
            upper = max(event.high for event in window)
            lower = min(event.low for event in window)

            if position is DonchianPosition.FLAT and events[index].close > upper:
                position = DonchianPosition.LONG
            elif position is DonchianPosition.LONG and events[index].close < lower:
                position = DonchianPosition.FLAT

            positions[index] = position

        return tuple(positions)
