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


@pytest.mark.parametrize("value", ["2026-01-01T00:00:00Z", 0, None])
def test_request_rejects_invalid_timestamp_runtime_types(value: object) -> None:
    with pytest.raises(ValueError, match="event_time must be a datetime"):
        ConfirmationRequest(
            signals={},
            event_time=value,  # type: ignore[arg-type]
            received_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            source_event_id="event-1",
        )


@pytest.mark.parametrize("value", [0, None, object()])
def test_request_rejects_invalid_source_event_id_runtime_types(value: object) -> None:
    with pytest.raises(ValueError, match="source_event_id must be a string"):
        ConfirmationRequest(
            signals={},
            event_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
            received_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            source_event_id=value,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("value", [[], None, object()])
def test_request_rejects_invalid_signals_runtime_types(value: object) -> None:
    with pytest.raises(ValueError, match="signals must be a mapping"):
        ConfirmationRequest(
            signals=value,  # type: ignore[arg-type]
            event_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
            received_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            source_event_id="event-1",
        )


@pytest.mark.parametrize("value", ["0.5", True, None, nan, inf])
def test_request_rejects_invalid_signal_value_runtime_types(value: object) -> None:
    with pytest.raises(
        ValueError, match="signals must contain only (numeric values|finite values)"
    ):
        ConfirmationRequest(
            signals={"trend": value},  # type: ignore[dict-item]
            event_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
            received_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            source_event_id="event-1",
        )


@pytest.mark.parametrize("value", ["confirmation-1", 0, None])
def test_output_rejects_invalid_confirmation_id_runtime_types(value: object) -> None:
    if isinstance(value, str):
        pytest.skip("valid control")
    with pytest.raises(ValueError, match="confirmation_id must be a string"):
        ConfirmationOutput(
            confirmed=True,
            score=0.5,
            event_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
            confirmation_id=value,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("value", ["0.5", True, None, nan, inf])
def test_output_rejects_invalid_score_runtime_types(value: object) -> None:
    with pytest.raises(ValueError, match="score must be (numeric|finite and within)"):
        ConfirmationOutput(
            confirmed=True,
            score=value,  # type: ignore[arg-type]
            event_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
            confirmation_id="confirmation-1",
        )


@pytest.mark.parametrize("value", ["2026-01-01T00:00:00Z", 0, None])
def test_request_rejects_invalid_received_at_runtime_types(value: object) -> None:
    with pytest.raises(ValueError, match="received_at must be a datetime"):
        ConfirmationRequest(
            signals={},
            event_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
            received_at=value,  # type: ignore[arg-type]
            source_event_id="event-1",
        )


@pytest.mark.parametrize("value", ["2026-01-01T00:00:00Z", 0, None])
def test_output_rejects_invalid_event_time_runtime_types(value: object) -> None:
    with pytest.raises(ValueError, match="event_time must be a datetime"):
        ConfirmationOutput(
            confirmed=True,
            score=0.5,
            event_time=value,  # type: ignore[arg-type]
            confirmation_id="confirmation-1",
        )
