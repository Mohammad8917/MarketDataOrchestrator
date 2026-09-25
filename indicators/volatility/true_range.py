"""FILE: indicators/volatility/true_range.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Compute one true-range value from high, low, and optional previous close.
LAYER: indicators
OWNS: Pure true-range calculation with no state or I/O.
DOES_NOT_OWN: ATR smoothing, data ingestion, persistence, analysis composition, strategy, decision, risk
DEPENDENCIES: stdlib:math
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

import math


def true_range(high: float, low: float, previous_close: float | None = None) -> float:
    """Return true range using Wilder's max-of-three definition."""

    values = (high, low) if previous_close is None else (high, low, previous_close)
    if not all(math.isfinite(float(value)) for value in values):
        raise ValueError("true-range inputs must be finite")
    if high < low:
        raise ValueError("high must be greater than or equal to low")

    if previous_close is None:
        return float(high - low)
    return float(max(high - low, abs(high - previous_close), abs(low - previous_close)))
