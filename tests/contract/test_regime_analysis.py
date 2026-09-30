"""FILE: tests/contract/test_regime_analysis.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-30
DATE_PERSIAN: 1405-07-08
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify deterministic point-in-time regime analysis composition and provenance.
LAYER: tests
OWNS: Verification of the regime analysis contract and evaluator behavior.
DOES_NOT_OWN: Production implementation, provider I/O, strategy, risk, or release approval.
DEPENDENCIES: datetime, regime.features.regime_features, analysis.regime_analysis, pytest
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timedelta, timezone

import pytest

from analysis.regime_analysis import DeterministicRegimeAnalysisEvaluator
from regime.features.regime_features import RegimeFeatureRequest

NOW = datetime(2026, 9, 30, tzinfo=timezone.utc)


def request(closes: tuple[float, ...]) -> RegimeFeatureRequest:
    times = tuple(NOW - timedelta(minutes=len(closes) - 1 - index) for index in range(len(closes)))
    return RegimeFeatureRequest(
        event_time=NOW,
        received_at=NOW,
        source_event_id="event-1",
        observation_end_time=NOW,
        closes=closes,
        observation_times=times,
        trend_lookback=4,
        volatility_short_lookback=2,
        volatility_long_lookback=4,
    )


def test_contract_identity() -> None:
    evaluator = DeterministicRegimeAnalysisEvaluator()
    assert evaluator.contract_id == "regime_analysis_boundary"
    assert evaluator.contract_version == "1.0.0"
    assert evaluator.methodology_id == "deterministic_regime_analysis_baseline"
    assert evaluator.methodology_version == "1.0.0"


def test_analysis_composes_all_regime_outputs() -> None:
    result = DeterministicRegimeAnalysisEvaluator().analyze(request((100.0, 101.0, 102.0, 103.0)))
    assert result.features.trend_score == 1.0
    assert result.classification.label == "trend_up"
    assert result.classification.confidence == 1.0
    assert result.uncertainty.uncertainty_score == 0.0
    assert result.volatility_state.volatility_score == result.features.volatility_score


def test_analysis_preserves_market_event_provenance() -> None:
    result = DeterministicRegimeAnalysisEvaluator().analyze(request((100.0, 100.0, 100.0, 100.0)))
    assert result.event_time == NOW
    assert result.received_at == NOW
    assert result.source_event_id == "event-1"
    assert result.features.source_event_id == "event-1"
    assert result.uncertainty.source_event_id == "event-1"
    assert result.volatility_state.source_event_id == "event-1"


def test_analysis_is_deterministic() -> None:
    first = DeterministicRegimeAnalysisEvaluator().analyze(request((100.0, 101.0, 100.0, 101.0)))
    second = DeterministicRegimeAnalysisEvaluator().analyze(request((100.0, 101.0, 100.0, 101.0)))
    assert first == second


def test_insufficient_history_is_rejected() -> None:
    with pytest.raises(ValueError, match="insufficient history"):
        DeterministicRegimeAnalysisEvaluator().analyze(request((100.0, 101.0, 102.0)))
