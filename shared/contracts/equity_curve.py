"""FILE: shared/contracts/equity_curve.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-25
DATE_PERSIAN: 1405-07-03
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Define the terminal EquityCurve protocol and minimal immutable implementation.
LAYER: shared
OWNS: Typed terminal output interface semantics and value invariants.
DOES_NOT_OWN: backtest execution, persistence, strategy logic, output formatting
DEPENDENCIES: dataclasses, datetime, decimal, typing
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Iterator, Protocol, runtime_checkable


@runtime_checkable
class EquityCurve(Protocol):
    """Terminal backtest output: aligned UTC timestamps and portfolio values."""

    @property
    def timestamps(self) -> tuple[datetime, ...]: ...

    @property
    def equity(self) -> tuple[Decimal, ...]: ...

    @property
    def drawdown(self) -> tuple[Decimal, ...]: ...

    def __len__(self) -> int: ...

    def __iter__(self) -> Iterator[Decimal]: ...


def _validate_lengths(
    timestamps: object,
    equity: object,
    drawdown: object,
) -> None:
    if not isinstance(timestamps, tuple):
        raise ValueError("timestamps must be a tuple")
    if not isinstance(equity, tuple):
        raise ValueError("equity must be a tuple")
    if not isinstance(drawdown, tuple):
        raise ValueError("drawdown must be a tuple")
    if not (len(timestamps) == len(equity) == len(drawdown)):
        raise ValueError("timestamps, equity, and drawdown must have equal length")


def _validate_timestamps(timestamps: tuple[datetime, ...]) -> None:
    for timestamp in timestamps:
        if not isinstance(timestamp, datetime):
            raise ValueError("timestamps must contain datetime values")
        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            raise ValueError("timestamps must be timezone-aware")
        if timestamp.utcoffset() != timezone.utc.utcoffset(timestamp):
            raise ValueError("timestamps must be UTC")


def _validate_equity(equity: tuple[Decimal, ...]) -> None:
    for value in equity:
        if not isinstance(value, Decimal) or not value.is_finite():
            raise ValueError("equity values must be finite Decimal values")
        if value <= 0:
            raise ValueError("equity values must be positive")


def _validate_drawdown(drawdown: tuple[Decimal, ...]) -> None:
    for value in drawdown:
        if not isinstance(value, Decimal) or not value.is_finite():
            raise ValueError("drawdown values must be finite Decimal values")
        if value > 0:
            raise ValueError("drawdown values cannot be positive")


def _validate_order(
    timestamps: tuple[datetime, ...],
    drawdown: tuple[Decimal, ...],
) -> None:
    if timestamps != tuple(sorted(timestamps)):
        raise ValueError("timestamps must be ordered ascending")
    if any(left >= right for left, right in zip(timestamps, timestamps[1:])):
        raise ValueError("timestamps must be strictly increasing")
    if timestamps and drawdown[0] != Decimal("0"):
        raise ValueError("first drawdown must be zero")


@dataclass(frozen=True, slots=True)
class EquityCurveData:
    """Minimal immutable EquityCurve implementation."""

    timestamps: tuple[datetime, ...]
    equity: tuple[Decimal, ...]
    drawdown: tuple[Decimal, ...]

    def __post_init__(self) -> None:
        _validate_lengths(self.timestamps, self.equity, self.drawdown)
        _validate_timestamps(self.timestamps)
        _validate_equity(self.equity)
        _validate_drawdown(self.drawdown)
        _validate_order(self.timestamps, self.drawdown)

    def __len__(self) -> int:
        return len(self.timestamps)

    def __iter__(self) -> Iterator[Decimal]:
        return iter(self.equity)
