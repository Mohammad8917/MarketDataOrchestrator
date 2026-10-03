"""FILE: strategy/evaluation/performance_metrics.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-29
DATE_PERSIAN: 1405-07-07
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Calculate deterministic terminal performance metrics from an EquityCurve.
LAYER: strategy
OWNS: Metric calculation semantics and local validation.
DOES_NOT_OWN: evidence finalization, decision, risk, signal persistence
DEPENDENCIES: decimal, shared.contracts.equity_curve, shared.contracts.performance_metrics
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from decimal import Decimal

from shared.contracts.equity_curve import EquityCurve
from shared.contracts.performance_metrics import PerformanceMetricsData


def calculate_performance_metrics(equity_curve: EquityCurve) -> PerformanceMetricsData:
    """Calculate deterministic return and drawdown metrics from an EquityCurve."""
    if not isinstance(equity_curve, EquityCurve):
        raise TypeError("equity_curve must satisfy EquityCurve")

    equity = equity_curve.equity
    if not isinstance(equity, tuple):
        raise TypeError("equity_curve.equity must be a tuple")
    if not equity:
        raise ValueError("equity_curve must contain at least one observation")
    if len(equity_curve) != len(equity):
        raise ValueError("equity_curve length must match equity values")
    if any(not isinstance(value, Decimal) or not value.is_finite() for value in equity):
        raise ValueError("equity_curve.equity must contain finite Decimal values")
    if any(value <= 0 for value in equity):
        raise ValueError("equity_curve.equity values must be positive")

    observations = len(equity)
    initial_equity = equity[0]
    final_equity = equity[-1]
    total_return = (final_equity - initial_equity) / initial_equity

    peak = initial_equity
    max_drawdown = Decimal("0")
    for value in equity:
        if value > peak:
            peak = value
        drawdown = (value - peak) / peak
        if drawdown < max_drawdown:
            max_drawdown = drawdown

    return PerformanceMetricsData(
        observations=observations,
        initial_equity=initial_equity,
        final_equity=final_equity,
        total_return=total_return,
        max_drawdown=max_drawdown,
    )
