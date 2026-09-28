"""Strategy-aware deterministic historical backtest engine."""

from __future__ import annotations

from decimal import Decimal
from typing import Protocol, runtime_checkable

from domain.market_data_event import MarketDataEvent
from shared.contracts.equity_curve import EquityCurve, EquityCurveData
from shared.contracts.market_bar import MarketBar
from strategy.trend.donchian import DonchianPosition


@runtime_checkable
class PositionStrategy(Protocol):
    """Boundary for deterministic position signal generation."""

    def signals(self, events: tuple[MarketBar, ...]) -> tuple[DonchianPosition, ...]: ...


class StrategyBacktestEngine:
    """Apply a signal at candle i to the return from i to i+1."""

    def __init__(self, initial_capital: Decimal = Decimal("1")) -> None:
        if not initial_capital.is_finite() or initial_capital <= 0:
            raise ValueError("initial_capital must be finite and positive")
        self._initial_capital = initial_capital

    def run(
        self,
        events: tuple[MarketDataEvent, ...],
        strategy: PositionStrategy,
    ) -> EquityCurve:
        """Run a strategy with strict next-bar execution semantics."""
        if len(events) < 2:
            raise ValueError("at least two events are required")
        if not isinstance(strategy, PositionStrategy):
            raise TypeError("strategy must implement PositionStrategy")

        bars = tuple(
            MarketBar(
                event_time=event.event_time,
                open=event.open,
                high=event.high,
                low=event.low,
                close=event.close,
                volume=event.volume,
            )
            for event in events
        )
        signals = strategy.signals(bars)
        if len(signals) != len(events):
            raise ValueError("strategy must emit one signal per event")

        equity: list[Decimal] = [self._initial_capital]
        for index in range(1, len(events)):
            previous_close = events[index - 1].close
            current_close = events[index].close
            position = signals[index - 1]

            if position is DonchianPosition.LONG:
                equity.append(equity[-1] * current_close / previous_close)
            elif position is DonchianPosition.FLAT:
                equity.append(equity[-1])
            else:
                raise ValueError("strategy emitted an unsupported position")

        peak = equity[0]
        drawdown: list[Decimal] = [Decimal("0")]
        for value in equity[1:]:
            peak = max(peak, value)
            drawdown.append((value / peak) - Decimal("1"))

        return EquityCurveData(
            timestamps=tuple(event.event_time for event in events),
            equity=tuple(equity),
            drawdown=tuple(drawdown),
        )
