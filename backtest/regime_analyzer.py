"""FILE: backtest/regime_analyzer.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-30
DATE_PERSIAN: 1405-07-08
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Replay deterministic regime analysis point-in-time across canonical historical market events.
LAYER: backtest
OWNS: Historical observation-window construction and deterministic regime-analysis replay.
DOES_NOT_OWN: strategy execution, provider I/O, persistence mutation, risk decisions, or future-data access.
DEPENDENCIES: dataclasses, domain.market_data_event, analysis.regime_analysis, regime.features.regime_features
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from dataclasses import dataclass

from analysis.regime_analysis import (
    DeterministicRegimeAnalysisEvaluator,
    RegimeAnalysisEvaluator,
    RegimeAnalysisOutput,
)
from domain.market_data_event import MarketDataEvent
from regime.features.regime_features import RegimeFeatureRequest

CONTRACT_ID = "backtest_regime_analysis_boundary"
CONTRACT_VERSION = "1.0.0"


@dataclass(frozen=True, slots=True)
class RegimeAnalysisReplayOutput:
    results: tuple[RegimeAnalysisOutput, ...]
    contract_version: str = CONTRACT_VERSION


class RegimeAnalysisReplay:
    """Replay deterministic regime analysis without future observations."""

    contract_id = CONTRACT_ID
    contract_version = CONTRACT_VERSION

    def __init__(
        self,
        evaluator: RegimeAnalysisEvaluator | None = None,
        *,
        trend_lookback: int = 20,
        volatility_short_lookback: int = 10,
        volatility_long_lookback: int = 30,
    ) -> None:
        self._evaluator = evaluator or DeterministicRegimeAnalysisEvaluator()
        if not isinstance(self._evaluator, RegimeAnalysisEvaluator):
            raise TypeError("evaluator must implement RegimeAnalysisEvaluator")
        self._trend_lookback = trend_lookback
        self._volatility_short_lookback = volatility_short_lookback
        self._volatility_long_lookback = volatility_long_lookback
        if trend_lookback < 2:
            raise ValueError("trend_lookback must be >= 2")
        if volatility_short_lookback < 2:
            raise ValueError("volatility_short_lookback must be >= 2")
        if volatility_long_lookback <= volatility_short_lookback:
            raise ValueError("volatility_long_lookback must exceed volatility_short_lookback")

    def run(
        self,
        events: object,
    ) -> RegimeAnalysisReplayOutput:
        if not isinstance(events, tuple):
            raise ValueError("events must be a tuple")
        if any(not isinstance(event, MarketDataEvent) for event in events):
            raise ValueError("events must contain only MarketDataEvent values")
        if not events:
            raise ValueError("events must not be empty")
        if any(
            current.event_time <= previous.event_time
            for previous, current in zip(events, events[1:])
        ):
            raise ValueError("events must be strictly ordered by event_time")

        minimum_history = max(
            self._trend_lookback,
            self._volatility_long_lookback,
        )
        if not isinstance(self._evaluator, RegimeAnalysisEvaluator):
            raise TypeError("evaluator must implement RegimeAnalysisEvaluator")

        if len(events) < minimum_history:
            raise ValueError("insufficient history for configured regime analysis")

        results: list[RegimeAnalysisOutput] = []
        for index in range(minimum_history - 1, len(events)):
            event = events[index]
            window = events[: index + 1]
            request = RegimeFeatureRequest(
                event_time=event.event_time,
                received_at=event.received_at,
                source_event_id=str(event.event_id),
                observation_end_time=event.event_time,
                closes=tuple(float(item.close) for item in window),
                observation_times=tuple(item.event_time for item in window),
                trend_lookback=self._trend_lookback,
                volatility_short_lookback=self._volatility_short_lookback,
                volatility_long_lookback=self._volatility_long_lookback,
            )
            output = self._evaluator.analyze(request)
            if not isinstance(output, RegimeAnalysisOutput):
                raise TypeError("evaluator must return RegimeAnalysisOutput")
            if output.event_time != request.event_time:
                raise ValueError("regime analysis output event_time must match request")
            if output.received_at != request.received_at:
                raise ValueError("regime analysis output received_at must match request")
            if output.source_event_id != request.source_event_id:
                raise ValueError("regime analysis output source_event_id must match request")
            results.append(output)

        return RegimeAnalysisReplayOutput(results=tuple(results))
