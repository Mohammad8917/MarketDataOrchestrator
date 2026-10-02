"""FILE: tests/unit/test_confirmation_replay.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-01
DATE_PERSIAN: 1405-07-09
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify point-in-time confirmation replay consumer behavior.
LAYER: tests
OWNS: Confirmation replay consumer verification.
DOES_NOT_OWN: methodology profitability, provider behavior, risk, decision finalization
DEPENDENCIES: backtest.confirmation_replay; composition.confirmation_contract; composition.deterministic_consensus
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timedelta, timezone

import pytest

from backtest.confirmation_replay import ConfirmationReplay
from composition.confirmation_contract import ConfirmationOutput, ConfirmationRequest
from composition.confirmation.deterministic_threshold import DeterministicThresholdConfirmation


def _request(offset: int, signals: dict[str, float]) -> ConfirmationRequest:
    timestamp = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=offset)
    return ConfirmationRequest(
        signals=signals,
        event_time=timestamp,
        received_at=timestamp,
        source_event_id=f"event-{offset}",
    )


def test_replays_in_strict_event_time_order() -> None:
    requests = (
        _request(0, {"a": 1.0, "b": 1.0}),
        _request(1, {"a": -1.0, "b": 1.0}),
        _request(2, {"a": -1.0, "b": -1.0}),
    )
    output = ConfirmationReplay().run(requests, DeterministicThresholdConfirmation())
    assert [item.confirmed for item in output.results] == [True, False, True]\n    assert [item.score for item in output.results] == [1.0, 0.0, -1.0]
    assert [item.event_time for item in output.results] == [item.event_time for item in requests]


def test_rejects_empty_or_non_monotonic_requests() -> None:
    with pytest.raises(ValueError):
        ConfirmationReplay().run((), DeterministicThresholdConfirmation())

    first = _request(1, {"a": 1.0})
    with pytest.raises(ValueError):
        ConfirmationReplay().run(
            (first, _request(0, {"a": 1.0})),
            DeterministicThresholdConfirmation(),
        )


def test_rejects_non_confirmation_consumer() -> None:
    with pytest.raises(TypeError):
        ConfirmationReplay().run(
            (_request(0, {"a": 1.0}),),
            object(),  # type: ignore[arg-type]
        )


class _WrongTimestampConfirmer:
    contract_id = "signal_confirmation_boundary"
    contract_version = "1.0.0"
    confirmation_id = "test"

    def confirm(self, request: ConfirmationRequest) -> ConfirmationOutput:
        return ConfirmationOutput(
            confirmed=True,
            score=1.0,
            event_time=request.received_at + timedelta(minutes=1),
            confirmation_id="test",
        )


def test_rejects_future_timestamp_from_consumer() -> None:
    with pytest.raises(ValueError):
        ConfirmationReplay().run(
            (_request(0, {"a": 1.0}),),
            _WrongTimestampConfirmer(),
        )
