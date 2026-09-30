from datetime import datetime, timezone
import math
import pytest

from regime.uncertainty.regime_uncertainty import (
    CONTRACT_ID,
    CONTRACT_VERSION,
    RegimeUncertaintyOutput,
    RegimeUncertaintyRequest,
)

NOW = datetime(2026, 9, 30, tzinfo=timezone.utc)

def test_request_accepts_bounded_confidence() -> None:
    value = RegimeUncertaintyRequest(0.75, NOW, NOW, "event-1")
    assert value.confidence == 0.75

@pytest.mark.parametrize("value", [-0.01, 1.01, math.nan, math.inf])
def test_request_rejects_invalid_confidence(value: float) -> None:
    with pytest.raises(ValueError, match="confidence"):
        RegimeUncertaintyRequest(value, NOW, NOW, "event-1")

def test_request_requires_provenance() -> None:
    with pytest.raises(ValueError, match="source_event_id"):
        RegimeUncertaintyRequest(0.5, NOW, NOW, "")

def test_request_requires_utc() -> None:
    with pytest.raises(ValueError, match="UTC"):
        RegimeUncertaintyRequest(0.5, datetime(2026, 9, 30), NOW, "event-1")

def test_output_preserves_boundary_identity() -> None:
    output = RegimeUncertaintyOutput(0.25, NOW, "event-1")
    assert output.uncertainty_score == 0.25
    assert output.event_time == NOW
    assert output.source_event_id == "event-1"

def test_contract_identity_is_stable() -> None:
    assert CONTRACT_ID == "regime_uncertainty_boundary"
    assert CONTRACT_VERSION == "1.0.0"

    
from regime.uncertainty.regime_uncertainty import (
    ConfidenceComplementUncertaintyEvaluator,
    RegimeUncertaintyEvaluator,
)


def test_baseline_evaluator_maps_confidence_to_uncertainty() -> None:
    request = RegimeUncertaintyRequest(0.75, NOW, NOW, "event-1")
    output = ConfidenceComplementUncertaintyEvaluator().assess(request)
    assert output.uncertainty_score == 0.25
    assert output.event_time == NOW
    assert output.source_event_id == "event-1"


def test_baseline_evaluator_implements_protocol() -> None:
    assert isinstance(
        ConfidenceComplementUncertaintyEvaluator(),
        RegimeUncertaintyEvaluator,
    )
