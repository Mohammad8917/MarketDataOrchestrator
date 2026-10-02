"""FILE: tests/unit/test_strategy_replay.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-02
RESPONSIBILITY: Verify deterministic Strategy replay ordering, delegation, and point-in-time alignment.
LAYER: tests
PYTHON: >=3.13
"""

from datetime import UTC, datetime, timedelta

import pytest

from backtest.strategy_replay import StrategyReplay
from shared.interfaces.strategy import StrategyOutput, StrategyRequest


class RecordingStrategy:
    contract_id = "test_strategy"
    contract_version = "1.0.0"
    strategy_id = "test"

    def __init__(self) -> None:
        self.requests: list[StrategyRequest] = []

    def evaluate(self, request: StrategyRequest) -> StrategyOutput:
        self.requests.append(request)
        return StrategyOutput(
            action="hold",
            strength=0.5,
            event_time=request.event_time,
            strategy_id=self.strategy_id,
        )


def request(minute: int) -> StrategyRequest:
    moment = datetime(2026, 10, 2, 9, 0, tzinfo=UTC) + timedelta(minutes=minute)
    return StrategyRequest(
        inputs={"evidence": 0.5},
        event_time=moment,
        received_at=moment,
        source_event_id=f"evt-{minute}",
    )


def test_strategy_replay_delegates_once_and_preserves_order() -> None:
    strategy = RecordingStrategy()
    requests = (request(0), request(1))
    result = StrategyReplay().run(requests, strategy)

    assert result.results == (
        StrategyOutput("hold", 0.5, requests[0].event_time, "test"),
        StrategyOutput("hold", 0.5, requests[1].event_time, "test"),
    )
    assert strategy.requests == list(requests)


def test_strategy_replay_rejects_empty_requests() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        StrategyReplay().run((), RecordingStrategy())


def test_strategy_replay_rejects_unsorted_requests() -> None:
    with pytest.raises(ValueError, match="strictly ordered"):
        StrategyReplay().run((request(1), request(0)), RecordingStrategy())


def test_strategy_replay_rejects_non_strategy() -> None:
    with pytest.raises(TypeError, match="strategy must implement Strategy"):
        StrategyReplay().run((request(0),), object())  # type: ignore[arg-type]


def test_strategy_replay_rejects_output_time_mismatch() -> None:
    class InvalidStrategy(RecordingStrategy):
        def evaluate(self, strategy_request: StrategyRequest) -> StrategyOutput:
            return StrategyOutput(
                action="hold",
                strength=0.5,
                event_time=strategy_request.event_time + timedelta(minutes=1),
                strategy_id=self.strategy_id,
            )

    with pytest.raises(ValueError, match="event_time must match"):
        StrategyReplay().run((request(0),), InvalidStrategy())
