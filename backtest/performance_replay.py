"""FILE: backtest/performance_replay.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Provide the canonical point-in-time Backtest performance-analysis boundary.
LAYER: backtest
OWNS: Performance-analysis replay delegation and immutable output wrapping.
DOES_NOT_OWN: strategy methodology, portfolio construction, cost, liquidity, risk, decision finalization, trading execution
DEPENDENCIES: shared.contracts.equity_curve, shared.contracts.performance_metrics, strategy.evaluation.performance_metrics
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from dataclasses import dataclass

from shared.contracts.equity_curve import EquityCurve
from shared.contracts.performance_metrics import PerformanceMetricsData
from strategy.evaluation.performance_metrics import calculate_performance_metrics


CONTRACT_ID = "backtest_performance_analysis_replay_boundary"
CONTRACT_VERSION = "1.0.0"


@dataclass(frozen=True, slots=True)
class PerformanceAnalysisReplayOutput:
    """Immutable canonical output of Backtest performance analysis."""

    metrics: PerformanceMetricsData
    contract_version: str = CONTRACT_VERSION


class PerformanceAnalysisReplay:
    """Delegate deterministic performance analysis through a Backtest boundary."""

    contract_id = CONTRACT_ID
    contract_version = CONTRACT_VERSION

    def run(self, equity_curve: EquityCurve) -> PerformanceAnalysisReplayOutput:
        """Calculate terminal metrics without introducing trading semantics."""
        if not isinstance(equity_curve, EquityCurve):
            raise TypeError("equity_curve must satisfy EquityCurve")
        metrics = calculate_performance_metrics(equity_curve)
        return PerformanceAnalysisReplayOutput(metrics=metrics)
