"""FILE: backtest/strategy_evaluator.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-29
DATE_PERSIAN: 1405-07-07
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Evaluate a historical strategy run into the canonical performance metrics boundary.
LAYER: backtest
OWNS: Strategy backtest execution to terminal performance-metrics conversion.
DOES_NOT_OWN: strategy implementation, strategy selection, execution semantics, persistence, provider transport, output formatting
DEPENDENCIES: decimal; domain.market_data_event; shared.contracts.performance_metrics; strategy.evaluation.performance_metrics
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from decimal import Decimal

from domain.market_data_event import MarketDataEvent
from shared.contracts.performance_metrics import PerformanceMetrics
from strategy.evaluation.performance_metrics import calculate_performance_metrics

from .strategy import HistoricalStrategy
from .strategy_engine import StrategyBacktestEngine


class StrategyEvaluator:
    """Convert one deterministic historical strategy run into terminal metrics."""

    def __init__(self, initial_capital: Decimal = Decimal("10000")) -> None:
        self._engine = StrategyBacktestEngine(initial_capital)

    def evaluate(
        self,
        events: tuple[MarketDataEvent, ...],
        strategy: HistoricalStrategy,
    ) -> PerformanceMetrics:
        """Run the strategy and return its canonical terminal metrics."""
        equity_curve = self._engine.run(events, strategy)
        return calculate_performance_metrics(equity_curve)
