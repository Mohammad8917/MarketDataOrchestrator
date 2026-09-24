"""FILE: backtest/engine.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-25
DATE_PERSIAN: 1405-07-03
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Define the typed BacktestEngine execution boundary.
LAYER: backtest
OWNS: BacktestEngine protocol and its input/output type contract.
DOES_NOT_OWN: backtest execution, persistence, strategy implementation, portfolio accounting, output formatting
DEPENDENCIES: typing, domain.market_data_event, shared.contracts.equity_curve
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""
from __future__ import annotations

from typing import Protocol

from domain.market_data_event import MarketDataEvent
from shared.contracts.equity_curve import EquityCurve


class BacktestEngine(Protocol):
    """Typed execution boundary for the first historical backtest path."""

    def run(self, events: tuple[MarketDataEvent, ...]) -> EquityCurve: ...
