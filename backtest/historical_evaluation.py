"""FILE: backtest/historical_evaluation.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
DATE_PERSIAN: 1405-07-10
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Validate and delegate one normalized market stream to a historical evaluation consumer.
LAYER: backtest
OWNS: stream identity validation, temporal ordering, and evaluation delegation.
DOES_NOT_OWN: provider transport, strategy methodology, performance calculation, cost, liquidity, risk, decision, execution, or profitability claims.
DEPENDENCIES: typing, domain.market_data_event, shared.contracts.performance_metrics
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from domain.market_data_event import MarketDataEvent
from shared.contracts.performance_metrics import PerformanceMetricsData


@runtime_checkable
class HistoricalEvaluator(Protocol):
    """Canonical callable shape for one normalized historical market stream."""

    def evaluate(self, events: tuple[MarketDataEvent, ...]) -> PerformanceMetricsData: ...


class MultiMarketHistoricalEvaluationHarness:
    """Validate a single point-in-time market stream before evaluation."""

    @staticmethod
    def _validate_stream(events: object) -> tuple[MarketDataEvent, ...]:
        if not isinstance(events, tuple):
            raise ValueError("events must be a tuple")
        if not all(isinstance(event, MarketDataEvent) for event in events):
            raise ValueError("events must contain only MarketDataEvent values")
        if not events:
            raise ValueError("events must not be empty")
        first = events[0]
        if any(
            current.event_time <= previous.event_time
            for previous, current in zip(events, events[1:])
        ):
            raise ValueError("events must be strictly ordered by event_time")
        if any(
            event.provider != first.provider
            or event.symbol != first.symbol
            or event.timeframe != first.timeframe
            for event in events[1:]
        ):
            raise ValueError("events must belong to one provider, symbol, and timeframe stream")
        return events

    def evaluate(
        self,
        events: object,
        evaluator: HistoricalEvaluator,
    ) -> PerformanceMetricsData:
        """Validate one normalized stream and delegate evaluation exactly once."""
        validated_events = self._validate_stream(events)
        if not isinstance(evaluator, HistoricalEvaluator):
            raise TypeError("evaluator must implement HistoricalEvaluator")
        output = evaluator.evaluate(validated_events)
        if not isinstance(output, PerformanceMetricsData):
            raise TypeError("evaluator must return PerformanceMetricsData")
        return output
