"""FILE: indicators/trend/sma.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Compute simple moving average from an immutable indicator request.
LAYER: indicators
OWNS: SMA parameter validation and deterministic rolling-average calculation.
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


class SimpleMovingAverage:
    """Deterministic simple moving-average implementation."""

    contract_id: ClassVar[str] = INDICATOR_CONTRACT_ID
    contract_version: ClassVar[str] = INDICATOR_CONTRACT_VERSION
    indicator_id: ClassVar[str] = "sma"

    def __init__(self, period: int) -> None:
        if period <= 0:
            raise ValueError("period must be positive")
        self._period = period

    @property
    def period(self) -> int:
        return self._period

    def calculate(self, request: IndicatorRequest) -> IndicatorOutput:
        try:
            close = request.series["close"]
        except KeyError as exc:
            raise ValueError("series must contain close") from exc

        if not close:
            raise ValueError("close series must not be empty")
        if len(close) < self._period:
            raise ValueError("close series is shorter than period")

        window = close[-self._period :]
        if not all(
            isinstance(value, (int, float)) and not isinstance(value, bool) for value in window
        ):
            raise ValueError("close series values must be finite numeric values")
        if not all(math.isfinite(float(value)) for value in window):
            raise ValueError("close series values must be finite numeric values")

        value = sum(window) / self._period
        if not math.isfinite(float(value)):
            raise ValueError("SMA result is non-finite")
        return IndicatorOutput(
            values={"sma": float(value)},
            event_time=request.event_time,
            indicator_id=self.indicator_id,
        )
