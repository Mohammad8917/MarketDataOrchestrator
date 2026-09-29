"""FILE: tests/contract/test_regime_feature_builder.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.2
DATE_GREGORIAN: 2026-09-29
DATE_PERSIAN: 1405-07-07
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify deterministic regime feature methodology calculations and temporal integrity.
LAYER: tests
OWNS: Runtime builder calculation and warm-up contract coverage.
DOES_NOT_OWN: strategy, risk, decision, provider I/O
DEPENDENCIES: datetime, pytest, regime.features.regime_feature_builder, regime.features.regime_features
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timedelta, timezone
from math import log

import pytest

from regime.features.regime_feature_builder import (
    DeterministicCloseReturnFeatureBuilder,
)
from regime.features.regime_features import RegimeFeatureRequest

NOW = datetime(2026, 9, 29, tzinfo=timezone.utc)


def request(
    closes: tuple[float, ...],
    *,
    trend_lookback: int = 4,
    volatility_short_lookback: int = 2,
    volatility_long_lookback: int = 4,
) -> RegimeFeatureRequest:
    times = tuple(
        NOW - timedelta(minutes=len(closes) - 1 - index)
        for index in range(len(closes))
    )
    return RegimeFeatureRequest(
        event_time=NOW,
        received_at=NOW,
        source_event_id="event-1",
        observation_end_time=NOW,
        closes=closes,
        observation_times=times,
        trend_lookback=trend_lookback,
        volatility_short_lookback=volatility_short_lookback,
        volatility_long_lookback=volatility_long_lookback,
    )


def test_monotonic_up_produces_full_upward_trend() -> None:
    result = DeterministicCloseReturnFeatureBuilder().build(
        request((100.0, 101.0, 102.0, 103.0))
    )
    assert result.trend_score == 1.0
    assert result.volatility_score < 0.0


def test_monotonic_down_produces_full_downward_trend() -> None:
    result = DeterministicCloseReturnFeatureBuilder().build(
        request((103.0, 102.0, 101.0, 100.0))
    )
    assert result.trend_score == -1.0


def test_balanced_direction_produces_zero_trend_score() -> None:
    result = DeterministicCloseReturnFeatureBuilder().build(
        request(
            (100.0, 101.0, 100.0, 101.0, 100.0),
            trend_lookback=5,
        )
    )
    assert result.trend_score == 0.0


def test_flat_series_produces_zero_scores() -> None:
    result = DeterministicCloseReturnFeatureBuilder().build(
        request((100.0, 100.0, 100.0, 100.0))
    )
    assert result.trend_score == 0.0
    assert result.volatility_score == 0.0


def test_short_volatility_above_long_baseline_is_positive() -> None:
    closes = (100.0, 100.1, 100.2, 100.3, 110.0)
    result = DeterministicCloseReturnFeatureBuilder().build(
        request(
            closes,
            trend_lookback=5,
            volatility_short_lookback=2,
            volatility_long_lookback=5,
        )
    )
    short_mean = abs(log(110.0 / 100.3))
    long_mean = (
        abs(log(100.1 / 100.0))
        + abs(log(100.2 / 100.1))
        + abs(log(100.3 / 100.2))
        + abs(log(110.0 / 100.3))
    ) / 4
    expected = (short_mean - long_mean) / (short_mean + long_mean)
    assert result.volatility_score == pytest.approx(expected)
    assert result.volatility_score > 0.0


def test_short_volatility_below_long_baseline_is_negative() -> None:
    closes = (100.0, 101.0, 102.0, 103.0, 103.0)
    result = DeterministicCloseReturnFeatureBuilder().build(
        request(
            closes,
            trend_lookback=5,
            volatility_short_lookback=2,
            volatility_long_lookback=5,
        )
    )
    assert result.volatility_score < 0.0


def test_insufficient_history_fails_deterministically() -> None:
    with pytest.raises(ValueError, match="insufficient history"):
        DeterministicCloseReturnFeatureBuilder().build(
            request((100.0, 101.0, 102.0))
        )


def test_future_boundary_is_rejected_by_temporal_contract() -> None:
    with pytest.raises(ValueError, match="final observation time"):
        RegimeFeatureRequest(
            event_time=NOW,
            received_at=NOW,
            source_event_id="event-1",
            observation_end_time=NOW,
            closes=(100.0, 101.0, 102.0),
            observation_times=(
                NOW - timedelta(minutes=2),
                NOW - timedelta(minutes=1),
                NOW + timedelta(minutes=1),
            ),
            trend_lookback=2,
            volatility_short_lookback=2,
            volatility_long_lookback=3,
        )


def test_result_preserves_point_in_time_provenance() -> None:
    result = DeterministicCloseReturnFeatureBuilder().build(
        request((100.0, 101.0, 102.0, 103.0))
    )
    assert result.event_time == NOW
    assert result.source_event_id == "event-1"
