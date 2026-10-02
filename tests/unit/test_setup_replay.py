"""FILE: tests/unit/test_setup_replay.py
RESPONSIBILITY: Verify deterministic setup replay consumer invariants.
"""

from datetime import datetime, timezone

import pytest

from backtest.setup_replay import SetupReplay
from shared.interfaces.setup import SetupOutput, SetupRequest


def _request(event_time: datetime, source_event_id: str) -> SetupRequest:
    return SetupRequest(
        inputs={"structure": 0.8, "momentum": 0.6},
        event_time=event_time,
        received_at=event_time,
        source_event_id=source_event_id,
    )


class _Setup:
    contract_id = "setup_evaluation_boundary"
    contract_version = "1.0.0"
    setup_id = "test_setup_v1"

    def __init__(self) -> None:
        self.requests: list[SetupRequest] = []

    def evaluate(self, request: SetupRequest) -> SetupOutput:
        self.requests.append(request)
        return SetupOutput(
            direction="bullish",
            strength=0.7,
            event_time=request.event_time,
            setup_id=self.setup_id,
        )


def test_replays_in_order_and_returns_immutable_results() -> None:
    first = _request(datetime(2026, 1, 1, tzinfo=timezone.utc), "e1")
    second = _request(datetime(2026, 1, 2, tzinfo=timezone.utc), "e2")
    setup = _Setup()

    output = SetupReplay().run((first, second), setup)

    assert output.results[0].event_time < output.results[1].event_time
    assert tuple(setup.requests) == (first, second)
    with pytest.raises(AttributeError):
        output.results = ()  # type: ignore[misc]


def test_rejects_empty_requests() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        SetupReplay().run((), _Setup())


def test_rejects_non_increasing_requests() -> None:
    request = _request(datetime(2026, 1, 1, tzinfo=timezone.utc), "e1")
    with pytest.raises(ValueError, match="strictly ordered"):
        SetupReplay().run((request, request), _Setup())


def test_rejects_setup_without_contract_protocol() -> None:
    class Invalid:
        pass

    request = _request(datetime(2026, 1, 1, tzinfo=timezone.utc), "e1")
    with pytest.raises(TypeError, match="implement Setup"):
        SetupReplay().run((request,), Invalid())  # type: ignore[arg-type]


def test_rejects_output_event_time_mismatch() -> None:
    request = _request(datetime(2026, 1, 1, tzinfo=timezone.utc), "e1")

    class InvalidOutput(_Setup):
        def evaluate(self, request: SetupRequest) -> SetupOutput:
            return SetupOutput(
                direction="bullish",
                strength=0.7,
                event_time=datetime(2026, 1, 2, tzinfo=timezone.utc),
                setup_id=self.setup_id,
            )

    with pytest.raises(ValueError, match="event_time"):
        SetupReplay().run((request,), InvalidOutput())
