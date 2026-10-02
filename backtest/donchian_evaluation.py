"""FILE: backtest/donchian_evaluation.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Compose the canonical Donchian backtest equity curve with deterministic performance analysis.
LAYER: backtest
OWNS: Backtest-to-performance composition only.
DOES_NOT_OWN: strategy methodology, cost, liquidity, risk, decision, execution, persistence, or profitability claims.
DEPENDENCIES: backtest.donchian_engine, backtest.performance_replay, domain.market_data_event, shared.contracts.performance_metrics
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from backtest.donchian_engine import DonchianBacktestEngine
from backtest.performance_replay import PerformanceAnalysisReplay
from domain.market_data_event import MarketDataEvent
from shared.contracts.performance_metrics import PerformanceMetricsData


@dataclass(frozen=True, slots=True)
class DonchianPerformanceEvaluator:
    """Evaluate Donchian historical equity using canonical performance metrics."""

    period: int = 20
    initial_equity: Decimal = Decimal("1")

    def evaluate(self, events: tuple[MarketDataEvent, ...]) -> PerformanceMetricsData:
        """Run the strategy-aware backtest, then analyze its terminal equity curve."""
        equity_curve = DonchianBacktestEngine(
            period=self.period,
            initial_equity=self.initial_equity,
        ).run(events)
        return PerformanceAnalysisReplay().run(equity_curve).metrics
