"""FILE: tests/contract/test_regime_features.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-09-29
DATE_PERSIAN: 1405-07-07
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify the canonical regime feature construction boundary and methodology inputs.
LAYER: tests
OWNS: Regime feature contract invariants, temporal guards, and methodology configuration guards.
DOES_NOT_OWN: feature calculation, indicator algorithms, strategy, decision, risk
DEPENDENCIES: datetime; pytest; regime.features.regime_features
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timedelta, timezone

import pytest

from regime.features.regime_features import (
    REGIME_FEATURE_CONTRACT_ID,
    REGIME_FEATURE_CONTRACT_VERSION,
    REGIME_FEATURE_METHODOLOGY_ID,
    REGIME_FEATURE_METHODOLOGY_VERSION,
    RegimeFeatureRequest,
    RegimeFeatureSet,
)

NOW = datetime(2026, 9, 29, tzinfo=timezone.utc)


def request(**overrides: object) -> RegimeFeatureRequest:
    values: dict[str, object] = {
        "event_time": NOW,
        "received_at": NOW,
        "source_event_id": "event-1",
        "observation_end_time": NOW,
        "closes": (100.0, 101.0, 102.0, 103.0),
        "observation_times": tuple(NOW - timedelta(minutes=3 - i) for i in range(4)),
        "trend_lookback": 4,
        "volatility_short_lookback": 2,
        "volatility_long_lookback": 4,
    }
    values.update(overrides)
    return RegimeFeatureRequest(**values)  # type: ignore[arg-type]


def test_identity() -> None:
    assert REGIME_FEATURE_CONTRACT_ID == "regime_feature_construction_boundary"
    assert REGIME_FEATURE_CONTRACT_VERSION == "1.0.0"
    assert REGIME_FEATURE_METHODOLOGY_ID == "deterministic_close_return_baseline"
    assert REGIME_FEATURE_METHODOLOGY_VERSION == "1.0.0"


def test_temporal_alignment() -> None:
    with pytest.raises(ValueError, match="equal length"):
        request(closes=(100.0,))
    with pytest.raises(ValueError, match="final observation time"):
        request(observation_times=(NOW - timedelta(minutes=3),) * 4)
    with pytest.raises(ValueError, match="strictly increasing"):
        request(
            observation_times=(
                NOW - timedelta(minutes=3),
                NOW - timedelta(minutes=2),
                NOW - timedelta(minutes=2),
                NOW,
            )
        )


def test_close_values_and_lookbacks_are_validated() -> None:
    with pytest.raises(ValueError, match="finite positive"):
        request(closes=(100.0, 0.0, 102.0, 103.0))
    with pytest.raises(ValueError, match="integer >= 2"):
        request(trend_lookback=1)
    with pytest.raises(ValueError, match="must exceed"):
        request(volatility_short_lookback=4, volatility_long_lookback=4)


def test_feature_set_bounds() -> None:
    result = RegimeFeatureSet(0.5, -0.25, NOW, "event-1")
    assert result.trend_score == 0.5
    assert result.volatility_score == -0.25


def test_feature_set_rejects_invalid_scores() -> None:
    for value in (float("nan"), float("inf"), -1.1, 1.1):
        with pytest.raises(ValueError):
            RegimeFeatureSet(value, 0.0, NOW, "event-1")


def test_received_at_before_event_time_is_rejected() -> None:
    with pytest.raises(ValueError, match="received_at must not precede event_time"):
        request(received_at=NOW - timedelta(minutes=1))
