"""FILE: indicators/volatility/atr.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Compute Wilder average true range from an immutable indicator request.
LAYER: indicators
OWNS: ATR parameter validation and deterministic Wilder smoothing of true ranges.
DOES_NOT_OWN: data ingestion, provider I/O, persistence, analysis composition, strategy, decision, risk
DEPENDENCIES: indicators.core.base; indicators.volatility.true_range
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
from indicators.volatility.true_range import true_range


class AverageTrueRange:
    """Deterministic Wilder average true-range implementation."""

    contract_id: ClassVar[str] = INDICATOR_CONTRACT_ID
    contract_version: ClassVar[str] = INDICATOR_CONTRACT_VERSION
    indicator_id: ClassVar[str] = "atr"

    def __init__(self, period: int) -> None:
        if period <= 0:
            raise ValueError("period must be positive")
        self._period = period

    @property
    def period(self) -> int:
        return self._period

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

        ranges = [
            true_range(
                float(high[index]),
                float(low[index]),
                None if index == 0 else float(close[index - 1]),
            )
            for index in range(len(close))
        ]
        atr = sum(ranges[: self._period]) / self._period
        for value in ranges[self._period :]:
            atr = ((atr * (self._period - 1)) + value) / self._period

        if not math.isfinite(atr):
            raise ValueError("ATR result is non-finite")
        return IndicatorOutput(
            values={"atr": float(atr)},
            event_time=request.event_time,
            indicator_id=self.indicator_id,
        )
