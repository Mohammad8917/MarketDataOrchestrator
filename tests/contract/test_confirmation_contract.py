"""FILE: tests/contract/test_confirmation_contract.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-01
DATE_PERSIAN: 1405-07-09
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify the immutable confirmation boundary and its invariants.
LAYER: tests
OWNS: Contract-level verification of signal confirmation.
DOES_NOT_OWN: confirmation methodology or trading decisions
DEPENDENCIES: composition.confirmation_contract
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timedelta, timezone
from math import inf, nan

import pytest

from composition.confirmation_contract import (
    CONFIRMATION_CONTRACT_ID,
    CONFIRMATION_CONTRACT_VERSION,
    ConfirmationOutput,
    ConfirmationRequest,
)


def test_contract_metadata_is_stable() -> None:
    assert CONFIRMATION_CONTRACT_ID == "signal_confirmation_boundary"
    assert CONFIRMATION_CONTRACT_VERSION == "1.0.0"


def test_request_accepts_utc_evidence() -> None:
    timestamp = datetime(2026, 1, 1, tzinfo=timezone.utc)
    request = ConfirmationRequest(
        signals={"trend": 0.5, "structure": -0.25},
        event_time=timestamp,
        received_at=timestamp,
        source_event_id="event-1",
    )
    assert request.signals["trend"] == 0.5


@pytest.mark.parametrize(
    "event_time",
    [
        datetime(2026, 1, 1),
        datetime(2026, 1, 1, tzinfo=timezone(timedelta(hours=1))),
    ],
)
def test_request_requires_utc_timestamp(event_time: datetime) -> None:
    with pytest.raises(ValueError):
        ConfirmationRequest(
            signals={},
            event_time=event_time,
            received_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            source_event_id="event-1",
        )


@pytest.mark.parametrize("value", [nan, inf, -inf, 1.1, -1.1])
def test_output_rejects_invalid_score(value: float) -> None:
    with pytest.raises(ValueError):
        ConfirmationOutput(
            confirmed=True,
            score=value,
            event_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
            confirmation_id="confirmation-1",
        )


def test_output_accepts_bounded_score() -> None:
    output = ConfirmationOutput(
        confirmed=True,
        score=1.0,
        event_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
        confirmation_id="confirmation-1",
    )
    assert output.contract_version == CONFIRMATION_CONTRACT_VERSION


def test_request_rejects_received_at_before_event_time() -> None:
    event_time = datetime(2026, 1, 1, 10, tzinfo=timezone.utc)
    received_at = datetime(2026, 1, 1, 9, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="received_at must not precede event_time"):
        ConfirmationRequest({}, event_time, received_at, "event-1")
