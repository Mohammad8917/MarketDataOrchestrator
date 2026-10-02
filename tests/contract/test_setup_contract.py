"""Verify the canonical setup evaluation contract invariants."""

from datetime import datetime, timezone
from typing import Any

import pytest

from shared.interfaces.setup import (
    SETUP_CONTRACT_VERSION,
    Setup,
    SetupOutput,
    SetupRequest,
)


class FakeSetup:
    contract_id = "setup_evaluation_boundary"
    contract_version = SETUP_CONTRACT_VERSION
    setup_id = "fake_setup"

    def evaluate(self, request: SetupRequest) -> SetupOutput:
        return SetupOutput("bullish", 0.75, request.event_time, self.setup_id)


def test_protocol_shape_is_runtime_checkable() -> None:
    assert isinstance(FakeSetup(), Setup)


def test_request_and_output_are_typed_and_immutable() -> None:
    now = datetime.now(timezone.utc)
    request = SetupRequest({"structure": 0.8}, now, now, "evt-1")
    output = FakeSetup().evaluate(request)
    assert output.contract_version == SETUP_CONTRACT_VERSION
    with pytest.raises(AttributeError):
        output.direction = "bearish"  # type: ignore[misc]


@pytest.mark.parametrize("field", ["event_time", "received_at"])
def test_request_rejects_naive_timestamps(field: str) -> None:
    now = datetime(2026, 10, 2, 10, 0)
    values: dict[str, Any] = {
        "inputs": {"structure": 0.8},
        "event_time": now.replace(tzinfo=timezone.utc),
        "received_at": now.replace(tzinfo=timezone.utc),
        "source_event_id": "evt-1",
    }
    values[field] = now
    with pytest.raises(ValueError, match="UTC"):
        SetupRequest(**values)


def test_request_rejects_empty_inputs() -> None:
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError, match="inputs"):
        SetupRequest({}, now, now, "evt-1")


@pytest.mark.parametrize("value", [float("inf"), float("-inf"), float("nan")])
def test_request_rejects_non_finite_inputs(value: float) -> None:
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError, match="finite"):
        SetupRequest({"signal": value}, now, now, "evt-1")


def test_request_rejects_received_at_before_event_time() -> None:
    event_time = datetime(2026, 10, 2, 10, 0, tzinfo=timezone.utc)
    received_at = datetime(2026, 10, 2, 9, 59, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="precede"):
        SetupRequest({"signal": 0.7}, event_time, received_at, "evt-1")


def test_request_rejects_blank_source_event_id() -> None:
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError, match="source_event_id"):
        SetupRequest({}, now, now, "")


def test_output_rejects_invalid_direction_and_setup_id() -> None:
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError, match="direction"):
        SetupOutput("sideways", 0.5, now, "fake")
    with pytest.raises(ValueError, match="setup_id"):
        SetupOutput("bullish", 0.5, now, "")


@pytest.mark.parametrize("strength", [-0.1, 1.1])
def test_output_rejects_invalid_strength(strength: float) -> None:
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError, match="strength"):
        SetupOutput("bullish", strength, now, "fake")
