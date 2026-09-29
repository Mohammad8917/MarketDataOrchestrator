"""FILE: regime/classification/rule_based_classifier.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-29
DATE_PERSIAN: 1405-07-07
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Classify a regime request using the canonical deterministic baseline rules.
LAYER: regime
OWNS: Feature validation, deterministic label mapping, and confidence calculation for this classifier.
DOES_NOT_OWN: feature construction, provider I/O, look-ahead data, strategy, decision, risk
DEPENDENCIES: regime.classification.regime_classifier; regime.classification.regime_labels; math
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

import math
from typing import ClassVar

from regime.classification.regime_classifier import (
    REGIME_CONTRACT_ID,
    REGIME_CONTRACT_VERSION,
    RegimeOutput,
    RegimeRequest,
)
from regime.classification.regime_labels import RegimeLabel


class RuleBasedRegimeClassifier:
    """Deterministic point-in-time baseline regime classifier."""

    contract_id: ClassVar[str] = REGIME_CONTRACT_ID
    contract_version: ClassVar[str] = REGIME_CONTRACT_VERSION
    regime_id: ClassVar[str] = "rule_based_baseline"

    def classify(self, request: RegimeRequest) -> RegimeOutput:
        trend_score = self._read_score(request, "trend_score")
        volatility_score = self._read_score(request, "volatility_score")

        if trend_score > 0.0:
            label = RegimeLabel.TREND_UP
            confidence = abs(trend_score)
            regime_id = "trend"
        elif trend_score < 0.0:
            label = RegimeLabel.TREND_DOWN
            confidence = abs(trend_score)
            regime_id = "trend"
        elif volatility_score < 0.0:
            label = RegimeLabel.RANGE_LOW_VOLATILITY
            confidence = abs(volatility_score)
            regime_id = "range"
        elif volatility_score > 0.0:
            label = RegimeLabel.RANGE_HIGH_VOLATILITY
            confidence = abs(volatility_score)
            regime_id = "range"
        else:
            label = RegimeLabel.UNKNOWN
            confidence = 0.0
            regime_id = "unknown"

        return RegimeOutput(
            label=label.value,
            confidence=confidence,
            event_time=request.event_time,
            regime_id=regime_id,
        )

    @staticmethod
    def _read_score(request: RegimeRequest, name: str) -> float:
        try:
            values = request.features[name]
        except KeyError as exc:
            raise ValueError(f"features must contain {name}") from exc

        if len(values) != 1:
            raise ValueError(f"{name} must contain exactly one value")

        value = values[0]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{name} must be numeric")
        numeric = float(value)
        if not math.isfinite(numeric) or not -1.0 <= numeric <= 1.0:
            raise ValueError(f"{name} must be finite and within [-1, 1]")
        return numeric
