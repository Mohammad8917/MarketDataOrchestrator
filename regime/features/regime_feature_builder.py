"""FILE: regime/features/regime_feature_builder.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.1
DATE_GREGORIAN: 2026-09-29
DATE_PERSIAN: 1405-07-07
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Build deterministic close-return regime features from point-in-time observations.
LAYER: regime
OWNS: Deterministic trend and volatility feature calculation defined by ADR-0034.
DOES_NOT_OWN: market-data transport, provider I/O, persistence, strategy, risk, or decision finalization
DEPENDENCIES: math, regime.features.regime_features
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

import math

from regime.features.regime_features import (
    REGIME_FEATURE_CONTRACT_ID,
    REGIME_FEATURE_CONTRACT_VERSION,
    REGIME_FEATURE_METHODOLOGY_ID,
    REGIME_FEATURE_METHODOLOGY_VERSION,
    RegimeFeatureRequest,
    RegimeFeatureSet,
)


class DeterministicCloseReturnFeatureBuilder:
    """Build the project-owned deterministic close-return regime baseline."""

    contract_id = REGIME_FEATURE_CONTRACT_ID
    contract_version = REGIME_FEATURE_CONTRACT_VERSION
    methodology_id = REGIME_FEATURE_METHODOLOGY_ID
    methodology_version = REGIME_FEATURE_METHODOLOGY_VERSION

    def build(self, request: RegimeFeatureRequest) -> RegimeFeatureSet:
        """Construct point-in-time trend and volatility scores."""
        required_history = max(
            request.trend_lookback,
            request.volatility_long_lookback,
        )
        if len(request.closes) < required_history:
            raise ValueError("insufficient history for configured lookbacks")

        trend_returns = self._log_returns(
            request.closes[-request.trend_lookback :],
        )
        trend_signs = sum(
            1 if value > 0.0 else -1 if value < 0.0 else 0 for value in trend_returns
        )
        trend_score = trend_signs / (request.trend_lookback - 1)

        short_returns = self._log_returns(
            request.closes[-request.volatility_short_lookback :],
        )
        long_returns = self._log_returns(
            request.closes[-request.volatility_long_lookback :],
        )
        short_mean_abs = self._mean_abs(short_returns)
        long_mean_abs = self._mean_abs(long_returns)
        denominator = short_mean_abs + long_mean_abs
        volatility_score = (
            (short_mean_abs - long_mean_abs) / denominator if denominator > 0.0 else 0.0
        )

        return RegimeFeatureSet(
            trend_score=trend_score,
            volatility_score=volatility_score,
            event_time=request.event_time,
            source_event_id=request.source_event_id,
        )

    @staticmethod
    def _log_returns(closes: tuple[float, ...]) -> tuple[float, ...]:
        return tuple(
            math.log(current / previous) for previous, current in zip(closes, closes[1:])
        )

    @staticmethod
    def _mean_abs(values: tuple[float, ...]) -> float:
        if not values:
            return 0.0
        return sum(abs(value) for value in values) / len(values)
