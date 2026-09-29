"""FILE: backtest/execution_simulator.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-29
DATE_PERSIAN: 1405-07-07
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Define deterministic next-bar execution semantics for historical backtests.
LAYER: backtest
OWNS: Position validation, temporal execution boundary, and close-to-close equity multiplier semantics.
DOES_NOT_OWN: strategy generation, portfolio sizing, persistence, provider transport, performance metrics, or live side effects.
DEPENDENCIES: decimal, typing, shared.contracts.market_bar
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from decimal import Decimal
from typing import Protocol, runtime_checkable

from shared.contracts.market_bar import MarketBar


@runtime_checkable
class ExecutionSimulator(Protocol):
    """Consumer-owned execution semantics used by historical backtests."""

    def equity_multiplier(
        self,
        position: int,
        previous_bar: MarketBar,
        current_bar: MarketBar,
    ) -> Decimal:
        """Return the equity multiplier produced by the position over one bar."""


class CloseToCloseExecutionSimulator:
    """Apply the existing deterministic close-to-close next-bar semantics."""

    def equity_multiplier(
        self,
        position: int,
        previous_bar: MarketBar,
        current_bar: MarketBar,
    ) -> Decimal:
        if not isinstance(position, int) or isinstance(position, bool):
            raise TypeError("position must be int")
        if position not in (0, 1):
            raise ValueError("position must be 0 or 1")
        if not isinstance(previous_bar, MarketBar) or not isinstance(
            current_bar, MarketBar
        ):
            raise TypeError("bars must be MarketBar instances")
        if current_bar.event_time <= previous_bar.event_time:
            raise ValueError("current_bar must be strictly later than previous_bar")

        if position == 0:
            return Decimal("1")

        return current_bar.close / previous_bar.close
