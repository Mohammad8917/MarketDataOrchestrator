"""Regression tests for the MTF structure contract temporal boundary."""

from datetime import UTC, datetime
from typing import cast

import pytest

from shared.contracts.market_structure import MarketStructureOutput
from shared.contracts.mtf_structure import (
    MtfStructureInput,
    MtfStructureObservation,
    MtfStructureOutput,
    MtfStructureRequest,
)


EVENT_TIME = datetime(2026, 10, 2, 13, tzinfo=UTC)
RECEIVED_AT = datetime(2026, 10, 2, 13, 1, tzinfo=UTC)


def _structure(
    *, source_event_id: str = "evt-1", event_time: datetime = EVENT_TIME
) -> MarketStructureOutput:
    return MarketStructureOutput(
        points=(),
        events=(),
        state=None,
        event_time=event_time,
        source_event_id=source_event_id,
    )


def _request(
    *, event_time: object = EVENT_TIME, received_at: object = RECEIVED_AT
) -> MtfStructureRequest:
    return MtfStructureRequest(
        inputs=(MtfStructureInput("1H", _structure()),),
        event_time=cast(datetime, event_time),
        received_at=cast(datetime, received_at),
        source_event_id="evt-1",
    )


@pytest.mark.parametrize("field", ["event_time", "received_at"])
def test_request_rejects_invalid_temporal_runtime_types(field: str) -> None:
    values: dict[str, object] = {
        "event_time": EVENT_TIME,
        "received_at": RECEIVED_AT,
    }
    values[field] = "2026-10-02T13:00:00Z"

    with pytest.raises(ValueError, match=f"{field} must be a datetime"):
        _request(**values)


def test_request_rejects_future_structure_observation() -> None:
    future = datetime(2026, 10, 2, 13, 1, tzinfo=UTC)

    with pytest.raises(ValueError, match="future observations"):
        MtfStructureRequest(
            inputs=(MtfStructureInput("1H", _structure(event_time=future)),),
            event_time=EVENT_TIME,
            received_at=RECEIVED_AT,
            source_event_id="evt-1",
        )


def test_request_rejects_source_event_mismatch() -> None:
    with pytest.raises(ValueError, match="source_event_id must match request"):
        MtfStructureRequest(
            inputs=(MtfStructureInput("1H", _structure(source_event_id="evt-2")),),
            event_time=EVENT_TIME,
            received_at=RECEIVED_AT,
            source_event_id="evt-1",
        )


def test_output_rejects_invalid_temporal_runtime_type() -> None:
    with pytest.raises(ValueError, match="event_time must be a datetime"):
        MtfStructureOutput(
            observations=(MtfStructureObservation("1H", "bullish"),),
            alignment="bullish",
            event_time=cast(datetime, "2026-10-02T13:00:00Z"),
            source_event_id="evt-1",
        )
