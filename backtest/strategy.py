"""FILE: backtest/strategy.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-29
DATE_PERSIAN: 1405-07-07
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Define the consumer-owned historical strategy execution protocol for backtests.
LAYER: backtest
OWNS: Historical strategy input/output protocol semantics required by backtest execution.
DOES_NOT_OWN: strategy implementations, strategy registry contracts, market-data persistence, portfolio policy, or metrics.
DEPENDENCIES: typing, shared.contracts.market_bar
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from shared.contracts.market_bar import MarketBar


@runtime_checkable
class PositionSignal(Protocol):
    """Minimal structural position value consumed by backtest execution."""

    @property
    def value(self) -> int: ...


@runtime_checkable
class HistoricalStrategy(Protocol):
    """Historical strategy protocol owned by the backtest consumer."""

    def signals(self, events: tuple[MarketBar, ...]) -> tuple[PositionSignal, ...]: ...
