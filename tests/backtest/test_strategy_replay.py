"""FILE: tests/backtest/test_strategy_replay.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-03
DATE_PERSIAN: 1405-07-11
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify fail-closed strategy replay validation and temporal output alignment.
LAYER: tests
OWNS: StrategyReplay runtime-boundary and temporal contract verification.
DOES_NOT_OWN: Strategy methodology or trading execution.
DEPENDENCIES: backtest.strategy_replay; shared.interfaces.strategy; pytest
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timedelta, timezone

import pytest

from backtest.strategy_replay import StrategyReplay
from shared.interfaces.strategy import StrategyOutput, StrategyRequest


def request(index: int) -> StrategyRequest:
    timestamp = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=index)
    return StrategyRequest(
        inputs={"x": 1.0},
        event_time=timestamp,
        received_at=timestamp,
        source_event_id=f"event-{index}",
    )


class ValidStrategy:
    contract_id = "test_strategy"
    contract_version = "1.0.0"
    strategy_id = "test"

    def evaluate(self, value: StrategyRequest) -> StrategyOutput:
        return StrategyOutput(
            action="WAIT",
            strength=0.5,
            event_time=value.event_time,
            strategy_id=self.strategy_id,
        )


def test_replays_ordered_requests() -> None:
    result = StrategyReplay().run((request(0), request(1)), ValidStrategy())
    assert len(result.results) == 2
    assert result.results[0].event_time < result.results[1].event_time


@pytest.mark.parametrize("requests", [[], None, "requests", [request(0)]])
def test_rejects_invalid_request_containers(requests: object) -> None:
    if isinstance(requests, list) and requests:
        with pytest.raises(ValueError, match="requests must be a tuple"):
            StrategyReplay().run(requests, ValidStrategy())  # type: ignore[arg-type]
    else:
        with pytest.raises(ValueError, match="requests must be a tuple|requests must not be empty"):
            StrategyReplay().run(requests, ValidStrategy())  # type: ignore[arg-type]


def test_rejects_invalid_request_element() -> None:
    with pytest.raises(ValueError, match="requests must contain only StrategyRequest"):
        StrategyReplay().run((request(0), object()), ValidStrategy())  # type: ignore[arg-type]


def test_rejects_non_strict_temporal_order() -> None:
    with pytest.raises(ValueError, match="strictly ordered"):
        StrategyReplay().run((request(1), request(0)), ValidStrategy())


def test_rejects_invalid_strategy() -> None:
    with pytest.raises(TypeError, match="must implement Strategy"):
        StrategyReplay().run((request(0),), object())  # type: ignore[arg-type]


def test_rejects_invalid_strategy_output_type() -> None:
    class InvalidOutputStrategy(ValidStrategy):
        def evaluate(self, value: StrategyRequest) -> object:
            return object()

    with pytest.raises(TypeError, match="must return StrategyOutput"):
        StrategyReplay().run((request(0),), InvalidOutputStrategy())


def test_rejects_temporally_misaligned_output() -> None:
    class MisalignedStrategy(ValidStrategy):
        def evaluate(self, value: StrategyRequest) -> StrategyOutput:
            return StrategyOutput(
                action="WAIT",
                strength=0.5,
                event_time=value.event_time + timedelta(minutes=1),
                strategy_id=self.strategy_id,
            )

    with pytest.raises(ValueError, match="event_time must match"):
        StrategyReplay().run((request(0),), MisalignedStrategy())
