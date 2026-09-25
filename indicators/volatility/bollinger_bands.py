"""FILE: indicators/volatility/bollinger_bands.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Compute Bollinger Bands from the canonical SMA implementation and population standard deviation.
LAYER: indicators
OWNS: Bollinger period/multiplier validation and deterministic band calculation.
DOES_NOT_OWN: data ingestion, provider I/O, persistence, analysis composition, strategy, decision, risk
DEPENDENCIES: indicators.core.base; indicators.trend.sma; stdlib:math
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
from indicators.trend.sma import SimpleMovingAverage


class BollingerBands:
    """Deterministic Bollinger Band implementation using SimpleMovingAverage."""

    contract_id: ClassVar[str] = INDICATOR_CONTRACT_ID
    contract_version: ClassVar[str] = INDICATOR_CONTRACT_VERSION
    indicator_id: ClassVar[str] = "bollinger"

    def __init__(self, period: int, multiplier: float = 2.0) -> None:
        if period <= 0:
            raise ValueError("period must be positive")
        if not math.isfinite(multiplier) or multiplier <= 0.0:
            raise ValueError("multiplier must be positive and finite")
        self._period = period
        self._multiplier = float(multiplier)
        self._sma = SimpleMovingAverage(period)

    @property
    def period(self) -> int:
        return self._period

    @property
    def multiplier(self) -> float:
        return self._multiplier

    def calculate(self, request: IndicatorRequest) -> IndicatorOutput:
        try:
            close = request.series["close"]
        except KeyError as exc:
            raise ValueError("series must contain close") from exc

        if not close:
            raise ValueError("close series must not be empty")
        if len(close) < self._period:
            raise ValueError("close series is shorter than period")

        values = list(close)
        if not all(
            isinstance(value, (int, float)) and not isinstance(value, bool) for value in values
        ):
            raise ValueError("close series values must be finite numeric values")
        if not all(math.isfinite(float(value)) for value in values):
            raise ValueError("close series values must be finite numeric values")

        window = values[-self._period :]
        mean = float(self._sma.calculate(request).values["sma"])
        variance = sum((float(value) - mean) ** 2 for value in window) / self._period
        standard_deviation = math.sqrt(variance)
        upper = mean + (self._multiplier * standard_deviation)
        lower = mean - (self._multiplier * standard_deviation)

        if not all(math.isfinite(value) for value in (mean, upper, lower)):
            raise ValueError("Bollinger result is non-finite")
        return IndicatorOutput(
            values={
                "middle": mean,
                "upper": upper,
                "lower": lower,
            },
            event_time=request.event_time,
            indicator_id=self.indicator_id,
        )
