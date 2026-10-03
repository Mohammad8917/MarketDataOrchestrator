"""Regression tests for the regime-analysis output temporal boundary."""

from datetime import UTC, datetime
from types import SimpleNamespace
from typing import cast

import pytest

from analysis.regime_analysis import RegimeAnalysisOutput
from regime.classification.regime_classifier import RegimeOutput
from regime.features.regime_features import RegimeFeatureSet
from regime.uncertainty.regime_uncertainty import RegimeUncertaintyOutput
from volatility.state.volatility_state import VolatilityStateOutput


EVENT_TIME = datetime(2026, 10, 2, 13, tzinfo=UTC)
RECEIVED_AT = datetime(2026, 10, 2, 13, 1, tzinfo=UTC)


def _output(
    *, event_time: object = EVENT_TIME, received_at: object = RECEIVED_AT
) -> RegimeAnalysisOutput:
    return RegimeAnalysisOutput(
        features=cast(
            RegimeFeatureSet,
            SimpleNamespace(event_time=EVENT_TIME, source_event_id="evt-1"),
        ),
        classification=cast(RegimeOutput, SimpleNamespace(event_time=EVENT_TIME)),
        uncertainty=cast(
            RegimeUncertaintyOutput,
            SimpleNamespace(event_time=EVENT_TIME, source_event_id="evt-1"),
        ),
        volatility_state=cast(
            VolatilityStateOutput,
            SimpleNamespace(
                event_time=EVENT_TIME,
                received_at=received_at,
                source_event_id="evt-1",
            ),
        ),
        event_time=cast(datetime, event_time),
        received_at=cast(datetime, received_at),
        source_event_id="evt-1",
    )


def test_regime_output_rejects_received_at_before_event_time() -> None:
    with pytest.raises(ValueError, match="received_at must not precede event_time"):
        _output(received_at=datetime(2026, 10, 2, 12, 59, tzinfo=UTC))


@pytest.mark.parametrize("field", ["event_time", "received_at"])
def test_regime_output_rejects_invalid_temporal_runtime_types(field: str) -> None:
    values: dict[str, object] = {
        "event_time": EVENT_TIME,
        "received_at": RECEIVED_AT,
    }
    values[field] = "2026-10-02T13:00:00Z"

    with pytest.raises(ValueError, match=f"{field} must be a datetime"):
        _output(**values)


def test_regime_output_accepts_equal_event_and_received_times() -> None:
    output = _output(received_at=EVENT_TIME)

    assert output.event_time == output.received_at == EVENT_TIME


@pytest.mark.parametrize("field", ["event_time", "received_at"])
def test_regime_output_rejects_non_utc_temporal_values(field: str) -> None:
    values: dict[str, object] = {
        "event_time": EVENT_TIME,
        "received_at": RECEIVED_AT,
    }
    values[field] = datetime(2026, 10, 2, 13, tzinfo=timezone(timedelta(hours=2)))
    with pytest.raises(ValueError, match=f"{field} must be timezone-aware UTC"):
        _output(**values)


def test_regime_output_rejects_empty_source_event_id() -> None:
    with pytest.raises(ValueError, match="source_event_id must be non-empty"):
        RegimeAnalysisOutput(
            features=cast(RegimeFeatureSet, SimpleNamespace(event_time=EVENT_TIME, source_event_id="evt-1")),
            classification=cast(RegimeOutput, SimpleNamespace(event_time=EVENT_TIME)),
            uncertainty=cast(RegimeUncertaintyOutput, SimpleNamespace(event_time=EVENT_TIME, source_event_id="evt-1")),
            volatility_state=cast(
                VolatilityStateOutput,
                SimpleNamespace(event_time=EVENT_TIME, received_at=RECEIVED_AT, source_event_id="evt-1"),
            ),
            event_time=EVENT_TIME,
            received_at=RECEIVED_AT,
            source_event_id="",
        )
