"""FILE: tests/contract/test_regime_features.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-29
DATE_PERSIAN: 1405-07-07
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify the canonical regime feature construction boundary.
LAYER: tests
OWNS: Regime feature contract invariants and temporal guards.
DOES_NOT_OWN: feature methodology, indicator algorithms, strategy, decision, risk
DEPENDENCIES: datetime; regime.features.regime_features
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timezone
from typing import cast

import pytest

from regime.features.regime_features import (
    REGIME_FEATURE_CONTRACT_ID,
    REGIME_FEATURE_CONTRACT_VERSION,
    RegimeFeatureRequest,
    RegimeFeatureSet,
)


NOW = datetime(2026, 9, 29, tzinfo=timezone.utc)


def test_feature_set_accepts_canonical_bounded_scores() -> None:
    result = RegimeFeatureSet(
        trend_score=0.75,
        volatility_score=-0.25,
        event_time=NOW,
        source_event_id="event-1",
    )

    assert result.trend_score == 0.75
    assert result.volatility_score == -0.25
    assert result.contract_version == REGIME_FEATURE_CONTRACT_VERSION


@pytest.mark.parametrize("field", ["trend_score", "volatility_score"])
@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf"), -1.01, 1.01, True])
def test_scores_must_be_finite_numeric_and_bounded(field: str, value: object) -> None:
    trend_score = 0.0
    volatility_score = 0.0
    if field == "trend_score":
        trend_score = cast(float, value)
    else:
        volatility_score = cast(float, value)
    with pytest.raises(ValueError):
        RegimeFeatureSet(
            trend_score=trend_score,
            volatility_score=volatility_score,
            event_time=NOW,
            source_event_id="event-1",
        )


def test_feature_set_rejects_empty_source_event_id() -> None:
    with pytest.raises(ValueError, match="source_event_id"):
        RegimeFeatureSet(
            trend_score=0.0,
            volatility_score=0.0,
            event_time=NOW,
            source_event_id="",
        )


def test_feature_request_enforces_utc_and_point_in_time_ordering() -> None:
    request = RegimeFeatureRequest(
        event_time=NOW,
        received_at=NOW,
        source_event_id="event-1",
        observation_end_time=NOW,
    )
    assert request.observation_end_time == request.event_time


def test_feature_request_rejects_future_observation() -> None:
    with pytest.raises(ValueError, match="observation_end_time"):
        RegimeFeatureRequest(
            event_time=NOW,
            received_at=NOW,
            source_event_id="event-1",
            observation_end_time=datetime(2026, 9, 29, 0, 0, 1, tzinfo=timezone.utc),
        )


def test_feature_request_rejects_non_utc_timestamps() -> None:
    with pytest.raises(ValueError, match="UTC"):
        RegimeFeatureRequest(
            event_time=NOW.replace(tzinfo=None),
            received_at=NOW,
            source_event_id="event-1",
            observation_end_time=NOW,
        )


def test_feature_request_contract_identity_is_stable() -> None:
    assert REGIME_FEATURE_CONTRACT_ID == "regime_feature_construction_boundary"
    assert REGIME_FEATURE_CONTRACT_VERSION == "1.0.0"
