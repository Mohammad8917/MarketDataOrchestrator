"""FILE: tests/backtest/test_setup_replay.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-03
DATE_PERSIAN: 1405-07-11
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify fail-closed setup replay validation and temporal output alignment.
LAYER: tests
OWNS: SetupReplay runtime-boundary and temporal contract verification.
DOES_NOT_OWN: Setup methodology or trading execution.
DEPENDENCIES: backtest.setup_replay; shared.interfaces.setup; pytest
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timedelta, timezone
from typing import cast

import pytest

from backtest.setup_replay import SetupReplay
from shared.interfaces.setup import SetupOutput, SetupRequest


def request(index: int = 0) -> SetupRequest:
    timestamp = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=index)
    return SetupRequest(
        inputs={"signal": 1.0},
        event_time=timestamp,
        received_at=timestamp,
        source_event_id=f"event-{index}",
    )


def output(value: SetupRequest) -> SetupOutput:
    return SetupOutput(
        direction="bullish",
        strength=1.0,
        event_time=value.event_time,
        setup_id="test-setup",
    )


class ValidSetup:
    contract_id = "test_setup"
    contract_version = "1.0.0"
    setup_id = "test-setup"

    def evaluate(self, value: SetupRequest) -> SetupOutput:
        return output(value)


def test_replays_ordered_requests() -> None:
    result = SetupReplay().run((request(0), request(1)), ValidSetup())
    assert result.results == (output(request(0)), output(request(1)))


@pytest.mark.parametrize("requests", [[], None, "requests"])
def test_rejects_invalid_request_containers(requests: object) -> None:
    with pytest.raises(ValueError, match="requests must be a tuple"):
        SetupReplay().run(requests, ValidSetup())  # type: ignore[arg-type]


def test_rejects_invalid_request_element() -> None:
    with pytest.raises(ValueError, match="requests must contain only SetupRequest"):
        SetupReplay().run((request(), object()), ValidSetup())  # type: ignore[arg-type]


def test_rejects_empty_requests() -> None:
    with pytest.raises(ValueError, match="requests must not be empty"):
        SetupReplay().run((), ValidSetup())


def test_rejects_non_strict_temporal_order() -> None:
    with pytest.raises(ValueError, match="strictly ordered"):
        SetupReplay().run((request(1), request(0)), ValidSetup())


def test_rejects_invalid_setup() -> None:
    with pytest.raises(TypeError, match="must implement Setup"):
        SetupReplay().run((request(),), object())  # type: ignore[arg-type]


def test_rejects_invalid_output_type() -> None:
    class InvalidSetup(ValidSetup):
        def evaluate(self, value: SetupRequest) -> SetupOutput:
            return cast(SetupOutput, object())

    with pytest.raises(TypeError, match="must return SetupOutput"):
        SetupReplay().run((request(),), InvalidSetup())


def test_rejects_temporally_misaligned_output() -> None:
    class MisalignedSetup(ValidSetup):
        def evaluate(self, value: SetupRequest) -> SetupOutput:
            return SetupOutput(
                direction="bullish",
                strength=1.0,
                event_time=value.event_time + timedelta(minutes=1),
                setup_id=self.setup_id,
            )

    with pytest.raises(ValueError, match="event_time must match"):
        SetupReplay().run((request(),), MisalignedSetup())
