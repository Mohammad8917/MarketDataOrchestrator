"""FILE: shared/contracts/equity_curve.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-25
DATE_PERSIAN: 1405-07-03
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Define the terminal EquityCurve output protocol for the first backtesting slice.
LAYER: shared
OWNS: Typed terminal output interface semantics.
DOES_NOT_OWN: backtest execution, persistence, strategy logic, output formatting
DEPENDENCIES: datetime, decimal, typing
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Protocol, runtime_checkable


@runtime_checkable
class EquityCurve(Protocol):
    """Terminal backtest output: aligned UTC timestamps and portfolio values."""

    timestamps: tuple[datetime, ...]
    equity: tuple[Decimal, ...]
    drawdown: tuple[Decimal, ...]

    def __len__(self) -> int: ...

    def __iter__(self): ...
