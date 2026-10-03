"""FILE: tests/backtest/test_composition_replay.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-03
DATE_PERSIAN: 1405-07-11
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify fail-closed composition replay validation and temporal output alignment.
LAYER: tests
OWNS: CompositionReplay runtime-boundary and temporal contract verification.
DOES_NOT_OWN: Composition methodology or trading execution.
DEPENDENCIES: backtest.composition_replay; composition.composer; pytest
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timedelta, timezone
from typing import cast

import pytest

from backtest.composition_replay import CompositionReplay
from composition.composer import CompositionOutput, CompositionRequest


def request(index: int = 0) -> CompositionRequest:
    timestamp = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=index)
    return CompositionRequest(
        signals={"x": 1.0},
        event_time=timestamp,
        received_at=timestamp,
        source_event_id=f"event-{index}",
    )


def output(value: CompositionRequest) -> CompositionOutput:
    return CompositionOutput(
        value=1.0,
        event_time=value.event_time,
        composition_id="test-composition",
    )


class ValidComposer:
    contract_id = "test_composition"
    contract_version = "1.0.0"
    composition_id = "test-composition"

    def compose(self, value: CompositionRequest) -> CompositionOutput:
        return output(value)


def test_replays_ordered_requests() -> None:
    result = CompositionReplay().run((request(0), request(1)), ValidComposer())
    assert result.results == (output(request(0)), output(request(1)))


@pytest.mark.parametrize("requests", [[], None, "requests"])
def test_rejects_invalid_request_containers(requests: object) -> None:
    with pytest.raises(ValueError, match="requests must be a tuple"):
        CompositionReplay().run(requests, ValidComposer())  # type: ignore[arg-type]


def test_rejects_invalid_request_element() -> None:
    with pytest.raises(ValueError, match="requests must contain only CompositionRequest"):
        CompositionReplay().run((request(), object()), ValidComposer())  # type: ignore[arg-type]


def test_rejects_empty_requests() -> None:
    with pytest.raises(ValueError, match="requests must not be empty"):
        CompositionReplay().run((), ValidComposer())


def test_rejects_non_strict_temporal_order() -> None:
    with pytest.raises(ValueError, match="strictly ordered"):
        CompositionReplay().run((request(1), request(0)), ValidComposer())


def test_rejects_invalid_composer() -> None:
    with pytest.raises(TypeError, match="must implement SignalComposer"):
        CompositionReplay().run((request(),), object())  # type: ignore[arg-type]


def test_rejects_invalid_composition_output_type() -> None:
    class InvalidOutputComposer:
        contract_id = "test_composition"
        contract_version = "1.0.0"
        composition_id = "test-composition"

        def compose(self, value: CompositionRequest) -> CompositionOutput:
            return cast(CompositionOutput, object())

    with pytest.raises(TypeError, match="must return CompositionOutput"):
        CompositionReplay().run((request(),), InvalidOutputComposer())


def test_rejects_temporally_misaligned_output() -> None:
    class MisalignedComposer(ValidComposer):
        def compose(self, value: CompositionRequest) -> CompositionOutput:
            return CompositionOutput(
                value=1.0,
                event_time=value.event_time + timedelta(minutes=1),
                composition_id=self.composition_id,
            )

    with pytest.raises(ValueError, match="event_time must match"):
        CompositionReplay().run((request(),), MisalignedComposer())
