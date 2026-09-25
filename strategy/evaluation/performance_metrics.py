"""FILE: strategy/evaluation/performance_metrics.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.2.0
DATE_GREGORIAN: 2026-09-25
DATE_PERSIAN: 1405-07-03
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Calculate deterministic performance metrics from a historical equity curve.
LAYER: strategy
OWNS: Total return, maximum drawdown, annualized Sharpe ratio, and positive-return rate calculations.
DOES_NOT_OWN: strategy selection, backtest execution, risk, persistence, provider transport
DEPENDENCIES: dataclasses, decimal, math, shared.contracts.equity_curve
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from math import sqrt

from shared.contracts.equity_curve import EquityCurve


@dataclass(frozen=True, slots=True)
class PerformanceMetrics:
    """Explicit, reproducible summary of a backtest equity curve."""

    total_return: Decimal
    max_drawdown: Decimal
    sharpe_ratio: Decimal | None
    positive_return_rate: Decimal

    @classmethod
    def from_equity(
        cls,
        curve: EquityCurve,
        *,
        periods_per_year: int,
    ) -> "PerformanceMetrics":
        if periods_per_year <= 0:
            raise ValueError("periods_per_year must be positive")
        equity = curve.equity
        if not equity:
            raise ValueError("equity must not be empty")
        if any(value <= 0 or not value.is_finite() for value in equity):
            raise ValueError("equity values must be finite and positive")

        total_return = (equity[-1] / equity[0]) - Decimal("1")

        peak = equity[0]
        max_drawdown = Decimal("0")
        returns: list[Decimal] = []
        for previous, current in zip(equity, equity[1:]):
            peak = max(peak, current)
            drawdown = (current / peak) - Decimal("1")
            max_drawdown = min(max_drawdown, drawdown)
            returns.append((current / previous) - Decimal("1"))

        if not returns:
            sharpe_ratio = None
            positive_return_rate = Decimal("0")
        else:
            mean = sum(returns, Decimal("0")) / Decimal(len(returns))
            variance = sum(((value - mean) ** 2 for value in returns), Decimal("0")) / Decimal(
                len(returns)
            )
            if variance == 0:
                sharpe_ratio = None
            else:
                sharpe_ratio = mean / variance.sqrt() * Decimal(str(sqrt(periods_per_year)))
            positive_return_rate = Decimal(sum(value > 0 for value in returns)) / Decimal(
                len(returns)
            )

        return cls(
            total_return=total_return,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            positive_return_rate=positive_return_rate,
        )
