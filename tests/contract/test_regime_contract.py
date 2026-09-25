"""FILE: tests/contract/test_regime_contract.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify the canonical regime classification contract invariants.
LAYER: tests
OWNS: Contract-level verification for regime_classification_boundary.
DOES_NOT_OWN: regime production behavior, strategy execution, decision finalization
DEPENDENCIES: pytest; regime.classification.regime_classifier
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

from regime.classification.regime_classifier import (
    REGIME_CONTRACT_ID,
    REGIME_CONTRACT_VERSION,
    RegimeClassifier,
    RegimeOutput,
    RegimeRequest,
)


class FakeRegimeClassifier:
    contract_id = REGIME_CONTRACT_ID
    contract_version = REGIME_CONTRACT_VERSION
    regime_id = "fake"

    def classify(self, request: RegimeRequest) -> RegimeOutput:
        return RegimeOutput(
            label="neutral",
            confidence=0.5,
            event_time=request.event_time,
            regime_id=self.regime_id,
        )


def test_protocol_shape_is_runtime_checkable() -> None:
    assert isinstance(FakeRegimeClassifier(), RegimeClassifier)


def test_request_and_output_are_typed_and_immutable() -> None:
    now = datetime.now(timezone.utc)
    request = RegimeRequest(
        features={"momentum": (1.0, 2.0)},
        event_time=now,
        received_at=now + timedelta(seconds=1),
        source_event_id="evt-1",
    )
    output = FakeRegimeClassifier().classify(request)
    assert output.contract_version == REGIME_CONTRACT_VERSION
    assert output.event_time == now
    with pytest.raises(AttributeError):
        output.label = "trend"  # type: ignore[misc]


@pytest.mark.parametrize("field", ["event_time", "received_at"])
def test_request_rejects_naive_timestamps(field: str) -> None:
    now = datetime(2026, 9, 24, 10, 0)
    values: dict[str, Any] = {
        "features": {"x": (1.0,)},
        "event_time": now.replace(tzinfo=timezone.utc),
        "received_at": now.replace(tzinfo=timezone.utc),
        "source_event_id": "evt-1",
    }
    values[field] = now
    with pytest.raises(ValueError, match="UTC"):
        RegimeRequest(**values)


def test_request_rejects_empty_source_event_id() -> None:
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError, match="source_event_id"):
        RegimeRequest(
            features={},
            event_time=now,
            received_at=now,
            source_event_id="",
        )


def test_output_rejects_empty_label_and_regime_id() -> None:
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError, match="label"):
        RegimeOutput("", 0.5, now, "fake")
    with pytest.raises(ValueError, match="regime_id"):
        RegimeOutput("neutral", 0.5, now, "")


@pytest.mark.parametrize("confidence", [-0.1, 1.1])
def test_output_rejects_invalid_confidence(confidence: float) -> None:
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError, match="confidence"):
        RegimeOutput(
            label="neutral",
            confidence=confidence,
            event_time=now,
            regime_id="fake",
        )
