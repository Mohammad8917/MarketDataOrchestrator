"""Runtime and temporal invariant tests for StrategyRequest."""

from datetime import datetime, timedelta, timezone

import pytest

from shared.interfaces.strategy import StrategyRequest


def _request(
    *, event_time: datetime, received_at: datetime, inputs: object = None
) -> StrategyRequest:
    return StrategyRequest(
        inputs={} if inputs is None else inputs,
        event_time=event_time,
        received_at=received_at,
        source_event_id="evt-1",
    )


def test_rejects_empty_inputs() -> None:
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="inputs must not be empty"):
        _request(event_time=now, received_at=now)


def test_rejects_received_at_before_event_time() -> None:
    event_time = datetime(2026, 1, 1, 0, 1, tzinfo=timezone.utc)
    received_at = event_time - timedelta(seconds=1)
    with pytest.raises(ValueError, match="received_at must not precede event_time"):
        _request(event_time=event_time, received_at=received_at, inputs={"x": 1.0})


def test_rejects_non_finite_inputs() -> None:
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="finite"):
        _request(event_time=now, received_at=now, inputs={"x": float("nan")})


def test_accepts_valid_request() -> None:
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    request = _request(event_time=now, received_at=now, inputs={"x": 1.0})
    assert request.source_event_id == "evt-1"
