"""FILE: backtest/donchian_engine.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Execute the canonical Donchian strategy over ordered historical market events.
LAYER: backtest
OWNS: strategy-aware position application, point-in-time equity construction, and drawdown derivation.
DOES_NOT_OWN: signal methodology, transaction-cost estimation, liquidity, risk sizing, persistence, provider I/O, or execution.
DEPENDENCIES: decimal, backtest.engine, strategy.trend.donchian, shared.contracts.equity_curve, shared.contracts.market_bar
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from backtest.engine import BacktestEngine
from domain.market_data_event import MarketDataEvent
from shared.contracts.equity_curve import EquityCurve, EquityCurveData
from shared.contracts.market_bar import MarketBar
from strategy.trend.donchian import DonchianPosition, DonchianStrategy


@dataclass(frozen=True, slots=True)
class DonchianBacktestEngine:
    """Run a long-only Donchian strategy with next-bar application semantics."""

    period: int = 20
    initial_equity: Decimal = Decimal("1")

    def __post_init__(self) -> None:
        if self.period < 2:
            raise ValueError("period must be at least 2")
        if not self.initial_equity.is_finite() or self.initial_equity <= 0:
            raise ValueError("initial_equity must be a positive finite Decimal")

    def run(self, events: tuple[MarketDataEvent, ...]) -> EquityCurve:
        """Build an equity curve without applying a signal to its own closing bar."""
        if not events:
            raise ValueError("events must not be empty")
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
        positions = DonchianStrategy(period=self.period).signals(bars)

        equity: list[Decimal] = [self.initial_equity]
        for index in range(1, len(events)):
            previous_equity = equity[-1]
            if positions[index - 1] is DonchianPosition.LONG:
                previous_close = events[index - 1].close
                current_close = events[index].close
                equity.append(previous_equity * current_close / previous_close)
            else:
                equity.append(previous_equity)

        drawdown: list[Decimal] = []
        peak: Decimal | None = None
        for value in equity:
            peak = value if peak is None else max(peak, value)
            drawdown.append(value / peak - Decimal("1"))

        return EquityCurveData(
            timestamps=tuple(event.event_time for event in events),
            equity=tuple(equity),
            drawdown=tuple(drawdown),
        )


assert isinstance(DonchianBacktestEngine(), BacktestEngine)
