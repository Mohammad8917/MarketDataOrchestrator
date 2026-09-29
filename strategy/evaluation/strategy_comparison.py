"""FILE: strategy/evaluation/strategy_comparison.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-29
DATE_PERSIAN: 1405-07-07
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Build deterministic named strategy performance comparisons from EquityCurves.
LAYER: strategy
OWNS: Comparison construction and deterministic name ordering.
DOES_NOT_OWN: strategy selection, backtest execution, persistence, or ranking policy.
DEPENDENCIES: collections.abc, shared.contracts.equity_curve, shared.contracts.strategy_comparison, strategy.evaluation.performance_metrics
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from collections.abc import Mapping

from shared.contracts.equity_curve import EquityCurve
from shared.contracts.strategy_comparison import StrategyComparisonData
from strategy.evaluation.performance_metrics import calculate_performance_metrics


def build_strategy_comparison(
    curves: Mapping[str, EquityCurve],
) -> StrategyComparisonData:
    """Calculate metrics for named curves in deterministic name order."""
    if not curves:
        raise ValueError("at least one strategy curve is required")

    entries = tuple(
        (name, calculate_performance_metrics(curves[name]))
        for name in sorted(curves)
    )
    return StrategyComparisonData(entries=entries)
