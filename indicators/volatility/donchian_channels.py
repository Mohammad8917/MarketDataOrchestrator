"""FILE: indicators/volatility/donchian_channels.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Compute Donchian high/low channels and current breakout direction.
LAYER: indicators
OWNS: Donchian window validation, channel calculation, and breakout classification.
DOES_NOT_OWN: data ingestion, provider I/O, persistence, analysis composition, strategy, decision, risk
DEPENDENCIES: indicators.core.base
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


class DonchianChannels:
    """Deterministic Donchian channel and breakout implementation."""

    contract_id: ClassVar[str] = INDICATOR_CONTRACT_ID
    contract_version: ClassVar[str] = INDICATOR_CONTRACT_VERSION
    indicator_id: ClassVar[str] = "donchian"

    def __init__(self, period: int) -> None:
        if period <= 0:
            raise ValueError("period must be positive")
        self._period = period

    def calculate(self, request: IndicatorRequest) -> IndicatorOutput:
        try:
            high = request.series["high"]
            low = request.series["low"]
            close = request.series["close"]
        except KeyError as exc:
            raise ValueError("series must contain high, low, and close") from exc

        if not high or not low or not close:
            raise ValueError("OHLC series must not be empty")
        if not (len(high) == len(low) == len(close)):
            raise ValueError("OHLC series must have equal lengths")
        if len(close) < self._period:
            raise ValueError("OHLC series is shorter than period")

        values = [list(series) for series in (high, low, close)]
        if not all(
            isinstance(value, (int, float)) and not isinstance(value, bool)
            for series in values
            for value in series
        ):
            raise ValueError("OHLC values must be finite numeric values")
        if not all(math.isfinite(float(value)) for series in values for value in series):
            raise ValueError("OHLC values must be finite numeric values")

        upper = max(float(value) for value in high[-self._period :])
        lower = min(float(value) for value in low[-self._period :])
        middle = (upper + lower) / 2.0

        breakout = 0.0
        if len(close) > self._period:
            prior_upper = max(float(value) for value in high[-self._period - 1 : -1])
            prior_lower = min(float(value) for value in low[-self._period - 1 : -1])
            current_close = float(close[-1])
            if current_close > prior_upper:
                breakout = 1.0
            elif current_close < prior_lower:
                breakout = -1.0

        return IndicatorOutput(
            values={
                "upper": upper,
                "lower": lower,
                "middle": middle,
                "breakout": breakout,
            },
            event_time=request.event_time,
            indicator_id=self.indicator_id,
        )
