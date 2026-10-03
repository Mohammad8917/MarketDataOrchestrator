"""FILE: tests/backtest/test_confirmation_replay.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-03
DATE_PERSIAN: 1405-07-11
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify fail-closed confirmation replay validation and temporal output alignment.
LAYER: tests
OWNS: ConfirmationReplay runtime-boundary and temporal contract verification.
DOES_NOT_OWN: Confirmation methodology or trading execution.
DEPENDENCIES: backtest.confirmation_replay; composition.confirmation_contract; pytest
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timedelta, timezone
from typing import cast

import pytest

from backtest.confirmation_replay import ConfirmationReplay
from composition.confirmation_contract import ConfirmationOutput, ConfirmationRequest


def request(index: int) -> ConfirmationRequest:
    timestamp = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=index)
    return ConfirmationRequest(
        signals={"x": 1.0},
        event_time=timestamp,
        received_at=timestamp,
        source_event_id=f"event-{index}",
    )


class ValidConfirmation:
    contract_id = "test_confirmation"
    contract_version = "1.0.0"
    confirmation_id = "test"

    def confirm(self, value: ConfirmationRequest) -> ConfirmationOutput:
        return ConfirmationOutput(
            confirmed=True,
            score=0.5,
            event_time=value.event_time,
            confirmation_id=self.confirmation_id,
        )


def test_replays_ordered_requests() -> None:
    result = ConfirmationReplay().run((request(0), request(1)), ValidConfirmation())
    assert len(result.results) == 2


@pytest.mark.parametrize("requests", [[], None, "requests"])
def test_rejects_invalid_request_containers(requests: object) -> None:
    with pytest.raises(ValueError, match="requests must be a tuple"):
        ConfirmationReplay().run(requests, ValidConfirmation())  # type: ignore[arg-type]


def test_rejects_invalid_request_element() -> None:
    with pytest.raises(ValueError, match="requests must contain only ConfirmationRequest"):
        ConfirmationReplay().run((request(0), object()), ValidConfirmation())  # type: ignore[arg-type]


def test_rejects_empty_requests() -> None:
    with pytest.raises(ValueError, match="requests must not be empty"):
        ConfirmationReplay().run((), ValidConfirmation())


def test_rejects_non_strict_temporal_order() -> None:
    with pytest.raises(ValueError, match="strictly ordered"):
        ConfirmationReplay().run((request(1), request(0)), ValidConfirmation())


def test_rejects_invalid_confirmer() -> None:
    with pytest.raises(TypeError, match="must implement SignalConfirmation"):
        ConfirmationReplay().run((request(0),), object())  # type: ignore[arg-type]


def test_rejects_invalid_confirmation_output_type() -> None:
    class InvalidOutputConfirmation:
        contract_id = "test_confirmation"
        contract_version = "1.0.0"
        confirmation_id = "test"

        def confirm(self, value: ConfirmationRequest) -> ConfirmationOutput:
            return cast(ConfirmationOutput, object())

    with pytest.raises(TypeError, match="must return ConfirmationOutput"):
        ConfirmationReplay().run((request(0),), InvalidOutputConfirmation())


def test_rejects_temporally_misaligned_output() -> None:
    class MisalignedConfirmation(ValidConfirmation):
        def confirm(self, value: ConfirmationRequest) -> ConfirmationOutput:
            return ConfirmationOutput(
                confirmed=True,
                score=0.5,
                event_time=value.event_time + timedelta(minutes=1),
                confirmation_id=self.confirmation_id,
            )

    with pytest.raises(ValueError, match="event_time must match"):
        ConfirmationReplay().run((request(0),), MisalignedConfirmation())
