"""FILE: backtest/engine.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-25
DATE_PERSIAN: 1405-07-03
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Define the typed BacktestEngine boundary and minimal buy-and-hold implementation.
LAYER: backtest
OWNS: BacktestEngine protocol and minimal historical equity-curve execution.
DOES_NOT_OWN: persistence, strategy implementation, portfolio policy, provider transport, output formatting
DEPENDENCIES: decimal, typing, domain.market_data_event, shared.contracts.equity_curve
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from decimal import Decimal
from typing import Protocol

from domain.market_data_event import MarketDataEvent
from shared.contracts.equity_curve import EquityCurve, EquityCurveData


class BacktestEngine(Protocol):
    """Typed execution boundary for the first historical backtest path."""

    def run(self, events: tuple[MarketDataEvent, ...]) -> EquityCurve: ...


class SimpleBacktestEngine:
    """Minimal one-unit buy-and-hold backtest implementation."""

    def run(self, events: tuple[MarketDataEvent, ...]) -> EquityCurve:
        timestamps = tuple(event.event_time for event in events)
        equity = tuple(event.close for event in events)

        drawdown_values: list[Decimal] = []
        peak: Decimal | None = None
        for value in equity:
            peak = value if peak is None else max(peak, value)
            drawdown_values.append((value / peak) - Decimal("1"))

        return EquityCurveData(
            timestamps=timestamps,
            equity=equity,
            drawdown=tuple(drawdown_values),
        )
