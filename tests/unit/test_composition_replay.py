"""FILE: tests/unit/test_composition_replay.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-01
DATE_PERSIAN: 1405-07-09
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify point-in-time composition replay consumer behavior.
LAYER: tests
OWNS: Composition replay consumer verification.
DOES_NOT_OWN: methodology profitability, provider behavior, confirmation, risk, decision finalization
DEPENDENCIES: backtest.composition_replay; composition.composer; composition.deterministic_mean
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timedelta, timezone

import pytest

from backtest.composition_replay import CompositionReplay
from composition.composer import CompositionOutput, CompositionRequest
from composition.deterministic_mean import DeterministicEqualWeightMean


def _request(offset: int, signals: dict[str, float]) -> CompositionRequest:
    timestamp = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=offset)
    return CompositionRequest(
        signals=signals,
        event_time=timestamp,
        received_at=timestamp,
        source_event_id=f"event-{offset}",
    )


def test_replays_in_strict_event_time_order() -> None:
    requests = (
        _request(0, {"a": 1.0, "b": -1.0}),
        _request(1, {"a": 1.0, "b": 1.0}),
        _request(2, {"a": -1.0, "b": -1.0}),
    )
    output = CompositionReplay().run(requests, DeterministicEqualWeightMean())
    assert [item.value for item in output.results] == [0.0, 1.0, -1.0]
    assert [item.event_time for item in output.results] == [item.event_time for item in requests]


def test_rejects_empty_or_non_monotonic_requests() -> None:
    with pytest.raises(ValueError):
        CompositionReplay().run((), DeterministicEqualWeightMean())

    first = _request(1, {"a": 1.0})
    with pytest.raises(ValueError):
        CompositionReplay().run(
            (first, _request(0, {"a": 1.0})),
            DeterministicEqualWeightMean(),
        )


def test_rejects_non_composition_consumer() -> None:
    with pytest.raises(TypeError):
        CompositionReplay().run(
            (_request(0, {"a": 1.0}),),
            object(),  # type: ignore[arg-type]
        )


class _WrongTimestampComposer:
    contract_id = "signal_composition_boundary"
    contract_version = "1.0.0"
    composition_id = "test"

    def compose(self, request: CompositionRequest) -> CompositionOutput:
        return CompositionOutput(
            value=1.0,
            event_time=request.received_at + timedelta(minutes=1),
            composition_id="test",
        )


def test_rejects_future_timestamp_from_consumer() -> None:
    with pytest.raises(ValueError):
        CompositionReplay().run(
            (_request(0, {"a": 1.0}),),
            _WrongTimestampComposer(),
        )
