"""FILE: shared/contracts/performance_metrics.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-29
DATE_PERSIAN: 1405-07-07
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Define the immutable terminal performance metrics contract for an EquityCurve.
LAYER: shared
OWNS: Typed performance metric output semantics and value invariants.
DOES_NOT_OWN: metric calculation, backtest execution, persistence, strategy logic
DEPENDENCIES: dataclasses, decimal, typing
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol, runtime_checkable


@runtime_checkable
class PerformanceMetrics(Protocol):
    """Terminal deterministic performance summary."""

    @property
    def observations(self) -> int: ...

    @property
    def initial_equity(self) -> Decimal: ...

    @property
    def final_equity(self) -> Decimal: ...

    @property
    def total_return(self) -> Decimal: ...

    @property
    def max_drawdown(self) -> Decimal: ...


@dataclass(frozen=True, slots=True)
class PerformanceMetricsData:
    """Immutable validated performance metrics."""

    observations: int
    initial_equity: Decimal
    final_equity: Decimal
    total_return: Decimal
    max_drawdown: Decimal

    def __post_init__(self) -> None:
        if isinstance(self.observations, bool) or not isinstance(self.observations, int):
            raise ValueError("observations must be a positive integer")
        if self.observations < 1:
            raise ValueError("observations must be a positive integer")

        for name, value in (
            ("initial_equity", self.initial_equity),
            ("final_equity", self.final_equity),
            ("total_return", self.total_return),
            ("max_drawdown", self.max_drawdown),
        ):
            if not isinstance(value, Decimal) or not value.is_finite():
                raise ValueError(f"{name} must be a finite Decimal value")

        if self.initial_equity <= 0 or self.final_equity <= 0:
            raise ValueError("equity values must be positive")

        if self.max_drawdown > 0:
            raise ValueError("max_drawdown cannot be positive")

        expected_return = (self.final_equity - self.initial_equity) / self.initial_equity
        if self.total_return != expected_return:
            raise ValueError("total_return does not match equity values")
