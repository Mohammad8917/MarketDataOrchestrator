"""FILE: backtest/strategy_engine.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-29
DATE_PERSIAN: 1405-07-07
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Execute a historical strategy against canonical market events with next-bar semantics.
LAYER: backtest
OWNS: Strategy replay, position validation, next-bar execution, and equity-curve construction.
DOES_NOT_OWN: strategy implementation, persistence, provider transport, performance metrics, or output formatting.
DEPENDENCIES: decimal, domain.market_data_event, shared.contracts.equity_curve, shared.contracts.market_bar, backtest.strategy
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from decimal import Decimal

from domain.market_data_event import MarketDataEvent
from shared.contracts.equity_curve import EquityCurve, EquityCurveData
from shared.contracts.market_bar import MarketBar
from .strategy import HistoricalStrategy, PositionSignal


class StrategyBacktestEngine:
    """Replay a historical strategy using close-to-close next-bar execution."""

    def __init__(self, initial_capital: Decimal = Decimal("10000")) -> None:
        if not isinstance(initial_capital, Decimal):
            raise TypeError("initial_capital must be Decimal")
        if not initial_capital.is_finite() or initial_capital <= 0:
            raise ValueError("initial_capital must be a positive finite Decimal")
        self._initial_capital = initial_capital

    def run(
        self,
        events: tuple[MarketDataEvent, ...],
        strategy: HistoricalStrategy,
    ) -> EquityCurve:
        if len(events) < 2:
            raise ValueError("at least 2 events are required")
        if not isinstance(strategy, HistoricalStrategy):
            raise TypeError("strategy must implement HistoricalStrategy")
        if any(
            current.event_time <= previous.event_time
            for previous, current in zip(events, events[1:])
        ):
            raise ValueError("events must be strictly ordered by event_time")

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
            raise ValueError("strategy must return exactly one signal per event")

        equity = [self._initial_capital]
        peak = self._initial_capital
        drawdown = [Decimal("0")]

        for index in range(1, len(events)):
            signal = signals[index - 1]
            if not isinstance(signal, PositionSignal):
                raise TypeError("strategy signals must implement PositionSignal")
            if not isinstance(signal.value, int) or isinstance(signal.value, bool) or signal.value not in (0, 1):
                raise ValueError("strategy position value must be 0 or 1")

            previous_close = events[index - 1].close
            current_close = events[index].close
            current_equity = equity[-1]
            if signal.value == 1:
                current_equity *= current_close / previous_close

            equity.append(current_equity)
            peak = max(peak, current_equity)
            drawdown.append((current_equity / peak) - Decimal("1"))

        return EquityCurveData(
            timestamps=tuple(event.event_time for event in events),
            equity=tuple(equity),
            drawdown=tuple(drawdown),
        )
