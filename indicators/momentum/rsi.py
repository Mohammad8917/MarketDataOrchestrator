"""FILE: indicators/momentum/rsi.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Compute Wilder-style relative strength index from an immutable indicator request.
LAYER: indicators
OWNS: RSI parameter validation and deterministic Wilder smoothing calculation.
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


class RelativeStrengthIndex:
    """Deterministic Wilder-style relative strength index implementation."""

    contract_id: ClassVar[str] = INDICATOR_CONTRACT_ID
    contract_version: ClassVar[str] = INDICATOR_CONTRACT_VERSION
    indicator_id: ClassVar[str] = "rsi"

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
        if len(close) <= self._period:
            raise ValueError("close series is shorter than period plus one")

        values = list(close)
        if not all(
            isinstance(value, (int, float)) and not isinstance(value, bool) for value in values
        ):
            raise ValueError("close series values must be finite numeric values")
        if not all(math.isfinite(float(value)) for value in values):
            raise ValueError("close series values must be finite numeric values")

        changes = [
            float(values[index]) - float(values[index - 1]) for index in range(1, len(values))
        ]
        gains = [max(change, 0.0) for change in changes]
        losses = [max(-change, 0.0) for change in changes]

        average_gain = sum(gains[: self._period]) / self._period
        average_loss = sum(losses[: self._period]) / self._period
        for index in range(self._period, len(changes)):
            average_gain = ((average_gain * (self._period - 1)) + gains[index]) / self._period
            average_loss = ((average_loss * (self._period - 1)) + losses[index]) / self._period

        if average_loss == 0.0:
            value = 100.0 if average_gain > 0.0 else 50.0
        elif average_gain == 0.0:
            value = 0.0
        else:
            relative_strength = average_gain / average_loss
            value = 100.0 - (100.0 / (1.0 + relative_strength))

        if not math.isfinite(value):
            raise ValueError("RSI result is non-finite")
        return IndicatorOutput(
            values={"rsi": float(value)},
            event_time=request.event_time,
            indicator_id=self.indicator_id,
        )
