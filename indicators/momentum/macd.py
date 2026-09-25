"""FILE: indicators/momentum/macd.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Compute MACD, signal line, and histogram from the canonical EMA implementation.
LAYER: indicators
OWNS: MACD parameter validation and deterministic EMA-derived line/signal/histogram calculation.
DOES_NOT_OWN: data ingestion, provider I/O, persistence, analysis composition, strategy, decision, risk
DEPENDENCIES: indicators.core.base; indicators.trend.ema
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

import math
from typing import ClassVar

from indicators.core.base import (
    INDICATOR_CONTRACT_ID,
    INDICATOR_CONTRACT_VERSION,
    IndicatorOutput,
    IndicatorRequest,
)
from indicators.trend.ema import ExponentialMovingAverage


class MovingAverageConvergenceDivergence:
    """Deterministic EMA-derived MACD implementation."""

    contract_id: ClassVar[str] = INDICATOR_CONTRACT_ID
    contract_version: ClassVar[str] = INDICATOR_CONTRACT_VERSION
    indicator_id: ClassVar[str] = "macd"

    def __init__(self, fast_period: int, slow_period: int, signal_period: int) -> None:
        if fast_period <= 0 or slow_period <= 0 or signal_period <= 0:
            raise ValueError("periods must be positive")
        if fast_period >= slow_period:
            raise ValueError("fast period must be shorter than slow period")
        self._fast_period = fast_period
        self._slow_period = slow_period
        self._signal_period = signal_period

    def calculate(self, request: IndicatorRequest) -> IndicatorOutput:
        try:
            close = request.series["close"]
        except KeyError as exc:
            raise ValueError("series must contain close") from exc

        if not close:
            raise ValueError("close series must not be empty")
        required_length = self._slow_period + self._signal_period - 1
        if len(close) < required_length:
            raise ValueError("close series is shorter than MACD warm-up")

        values = list(close)
        if not all(
            isinstance(value, (int, float)) and not isinstance(value, bool) for value in values
        ):
            raise ValueError("close series values must be finite numeric values")
        if not all(math.isfinite(float(value)) for value in values):
            raise ValueError("close series values must be finite numeric values")

        fast_ema = ExponentialMovingAverage(self._fast_period)
        slow_ema = ExponentialMovingAverage(self._slow_period)
        macd_values: list[float] = []
        for end in range(self._slow_period, len(values) + 1):
            prefix = values[:end]
            prefix_request = IndicatorRequest(
                series={"close": prefix},
                event_time=request.event_time,
                received_at=request.received_at,
                source_event_id=request.source_event_id,
            )
            fast_value = fast_ema.calculate(prefix_request).values["ema"]
            slow_value = slow_ema.calculate(prefix_request).values["ema"]
            macd_values.append(float(fast_value - slow_value))

        signal_request = IndicatorRequest(
            series={"close": macd_values},
            event_time=request.event_time,
            received_at=request.received_at,
            source_event_id=request.source_event_id,
        )
        signal_value = (
            ExponentialMovingAverage(self._signal_period).calculate(signal_request).values["ema"]
        )
        macd_value = macd_values[-1]
        histogram = macd_value - float(signal_value)

        if not all(math.isfinite(value) for value in (macd_value, signal_value, histogram)):
            raise ValueError("MACD result is non-finite")
        return IndicatorOutput(
            values={
                "macd": macd_value,
                "signal": float(signal_value),
                "histogram": float(histogram),
            },
            event_time=request.event_time,
            indicator_id=self.indicator_id,
        )
