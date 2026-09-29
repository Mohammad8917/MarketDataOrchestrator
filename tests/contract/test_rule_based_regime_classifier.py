"""FILE: tests/contract/test_rule_based_regime_classifier.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-29
DATE_PERSIAN: 1405-07-07
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify deterministic rule-based regime classification semantics.
LAYER: tests
OWNS: Classifier contract and behavioral verification.
DOES_NOT_OWN: feature construction, strategy, decision, risk
DEPENDENCIES: datetime; regime.classification.regime_classifier; regime.classification.rule_based_classifier
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timezone

import pytest

from regime.classification.regime_classifier import RegimeRequest
from regime.classification.rule_based_classifier import RuleBasedRegimeClassifier


def request(trend: float, volatility: float) -> RegimeRequest:
    now = datetime(2026, 9, 29, tzinfo=timezone.utc)
    return RegimeRequest(
        features={"trend_score": (trend,), "volatility_score": (volatility,)},
        event_time=now,
        received_at=now,
        source_event_id="event-1",
    )


@pytest.mark.parametrize(
    ("trend", "volatility", "label", "regime_id", "confidence"),
    [
        (0.8, 0.2, "trend_up", "trend", 0.8),
        (-0.6, 0.9, "trend_down", "trend", 0.6),
        (0.0, -0.7, "range_low_volatility", "range", 0.7),
        (0.0, 0.4, "range_high_volatility", "range", 0.4),
        (0.0, 0.0, "unknown", "unknown", 0.0),
    ],
)
def test_classification_is_deterministic(
    trend: float,
    volatility: float,
    label: str,
    regime_id: str,
    confidence: float,
) -> None:
    output = RuleBasedRegimeClassifier().classify(request(trend, volatility))
    assert output.label == label
    assert output.regime_id == regime_id
    assert output.confidence == confidence


def test_trend_evidence_has_precedence_over_volatility() -> None:
    output = RuleBasedRegimeClassifier().classify(request(0.1, -1.0))
    assert output.label == "trend_up"
    assert output.confidence == 0.1


@pytest.mark.parametrize(
    ("feature", "value"),
    [
        ("trend_score", 1.1),
        ("trend_score", -1.1),
        ("volatility_score", float("nan")),
        ("volatility_score", float("inf")),
    ],
)
def test_scores_must_be_finite_and_bounded(feature: str, value: float) -> None:
    features = {"trend_score": (0.0,), "volatility_score": (0.0,)}
    features[feature] = (value,)
    with pytest.raises(ValueError):
        RuleBasedRegimeClassifier().classify(
            RegimeRequest(
                features=features,
                event_time=datetime(2026, 9, 29, tzinfo=timezone.utc),
                received_at=datetime(2026, 9, 29, tzinfo=timezone.utc),
                source_event_id="event-1",
            )
        )


@pytest.mark.parametrize("feature", ["trend_score", "volatility_score"])
def test_required_scores_must_be_present(feature: str) -> None:
    features = {"trend_score": (0.0,), "volatility_score": (0.0,)}
    del features[feature]
    with pytest.raises(ValueError):
        RuleBasedRegimeClassifier().classify(
            RegimeRequest(
                features=features,
                event_time=datetime(2026, 9, 29, tzinfo=timezone.utc),
                received_at=datetime(2026, 9, 29, tzinfo=timezone.utc),
                source_event_id="event-1",
            )
        )
