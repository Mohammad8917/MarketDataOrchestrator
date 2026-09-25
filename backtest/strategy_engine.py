"""FILE: backtest/strategy_engine.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.2.0
DATE_GREGORIAN: 2026-09-25
DATE_PERSIAN: 1405-07-03
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Execute shared-contract strategies against canonical historical market events.
LAYER: backtest
OWNS: Event-to-bar adaptation, next-bar position application, and historical equity-curve execution.
DOES_NOT_OWN: provider transport, strategy logic, persistence, live execution, risk policy
DEPENDENCIES: decimal, typing, domain.market_data_event, shared.contracts.equity_curve, shared.contracts.market_bar, strategy.trend.donchian
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from decimal import Decimal
from typing import Protocol, runtime_checkable

from domain.market_data_event import MarketDataEvent
from shared.contracts.equity_curve import EquityCurve, EquityCurveData
from shared.contracts.market_bar import MarketBar
from strategy.trend.donchian import DonchianPosition


@runtime_checkable
class PositionStrategy(Protocol):
    """Strategy boundary for deterministic historical execution."""

    def signals(self, events: tuple[MarketBar, ...]) -> tuple[DonchianPosition, ...]: ...


class StrategyBacktestEngine:
    """Apply a long/flat strategy signal to the following bar return."""

    def __init__(self, initial_capital: Decimal = Decimal("1")) -> None:
        if not initial_capital.is_finite() or initial_capital <= 0:
            raise ValueError("initial_capital must be finite and positive")
        self._initial_capital = initial_capital

    def run(
        self,
        events: tuple[MarketDataEvent, ...],
        strategy: PositionStrategy,
    ) -> EquityCurve:
        """Run signals generated at candle i over the return to candle i+1."""
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
