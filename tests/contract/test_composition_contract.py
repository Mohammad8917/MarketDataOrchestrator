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


def test_request_rejects_received_at_before_event_time() -> None:
    event_time = datetime(2026, 9, 24, 10, tzinfo=timezone.utc)
    received_at = datetime(2026, 9, 24, 9, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="received_at must not precede event_time"):
        CompositionRequest({"trend": 0.8}, event_time, received_at, "evt-1")


@pytest.mark.parametrize("value", [[], None, 0])
def test_request_rejects_invalid_signals_runtime_types(value: object) -> None:
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError, match="signals must be a mapping"):
        CompositionRequest(value, now, now, "evt-1")  # type: ignore[arg-type]


def test_request_rejects_empty_signals() -> None:
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError, match="signals must not be empty"):
        CompositionRequest({}, now, now, "evt-1")


@pytest.mark.parametrize("value", [True, "0.5", None, float("nan"), float("inf")])
def test_request_rejects_invalid_signal_values(value: object) -> None:
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError, match="signals must contain only (numeric|finite) values"):
        CompositionRequest({"trend": value}, now, now, "evt-1")  # type: ignore[dict-item]


@pytest.mark.parametrize("value", ["", "   ", 0, None])
def test_request_rejects_invalid_source_event_id_runtime_types(value: object) -> None:
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError, match="source_event_id"):
        CompositionRequest({"trend": 0.8}, now, now, value)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", ["2026-09-24T10:00:00Z", 0, None])
def test_request_rejects_invalid_timestamp_runtime_types(value: object) -> None:
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError, match="event_time must be a datetime"):
        CompositionRequest({"trend": 0.8}, value, now, "evt-1")  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [True, "0.5", None, float("nan"), float("inf")])
def test_output_rejects_invalid_value_runtime_types(value: object) -> None:
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError, match="value must be (numeric|finite)"):
        CompositionOutput(value, now, "average")  # type: ignore[arg-type]


@pytest.mark.parametrize("value", ["", "   ", 0, None])
def test_output_rejects_invalid_composition_id_runtime_types(value: object) -> None:
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError, match="composition_id"):
        CompositionOutput(0.5, now, value)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", ["", "   ", 0, None])
def test_output_rejects_invalid_contract_version_runtime_types(value: object) -> None:
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError, match="contract_version"):
        CompositionOutput(0.5, now, "average", value)  # type: ignore[arg-type]
