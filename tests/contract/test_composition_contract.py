"""FILE: tests/contract/test_composition_contract.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify the canonical signal composition contract invariants.
LAYER: tests
OWNS: Contract-level verification for signal_composition_boundary.
DOES_NOT_OWN: composition production behavior, strategy execution, decision finalization
DEPENDENCIES: pytest; composition.composer
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timezone
from typing import Any

import pytest

from composition.composer import (
    COMPOSITION_CONTRACT_VERSION,
    CompositionOutput,
    CompositionRequest,
    SignalComposer,
)


class FakeComposer:
    contract_id = "signal_composition_boundary"
    contract_version = COMPOSITION_CONTRACT_VERSION
    composition_id = "average"

    def compose(self, request: CompositionRequest) -> CompositionOutput:
        value = sum(request.signals.values()) / len(request.signals)
        return CompositionOutput(
            value=value, event_time=request.event_time, composition_id=self.composition_id
        )


def test_protocol_shape_is_runtime_checkable() -> None:
    assert isinstance(FakeComposer(), SignalComposer)


def test_output_rejects_empty_composition_id() -> None:
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError, match="composition_id"):
        CompositionOutput(0.0, now, "")


def test_request_and_output_are_typed_and_immutable() -> None:
    now = datetime.now(timezone.utc)
    request = CompositionRequest(
        signals={"trend": 0.8, "momentum": 0.4},
        event_time=now,
        received_at=now,
        source_event_id="evt-1",
    )
    output = FakeComposer().compose(request)
    assert output.value == pytest.approx(0.6)
    with pytest.raises(AttributeError):
        output.value = 1.0  # type: ignore[misc]


@pytest.mark.parametrize("field", ["event_time", "received_at"])
def test_request_rejects_naive_timestamps(field: str) -> None:
    now = datetime(2026, 9, 24, 10, 0)
    values: dict[str, Any] = {
        "signals": {"trend": 0.8},
        "event_time": now.replace(tzinfo=timezone.utc),
        "received_at": now.replace(tzinfo=timezone.utc),
        "source_event_id": "evt-1",
    }
    values[field] = now
    with pytest.raises(ValueError, match="UTC"):
        CompositionRequest(**values)


def test_request_rejects_empty_source_event_id() -> None:
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError, match="source_event_id"):
        CompositionRequest(signals={}, event_time=now, received_at=now, source_event_id="")
