"""Regression coverage for market-structure temporal runtime validation."""

from datetime import UTC, datetime
from decimal import Decimal
from typing import cast

import pytest

from shared.contracts.market_structure import (
    MarketStructureBar,
    MarketStructureOutput,
    MarketStructureRequest,
)

EVENT_TIME = datetime(2026, 10, 2, 13, tzinfo=UTC)
RECEIVED_AT = datetime(2026, 10, 2, 13, 1, tzinfo=UTC)


def _bar() -> MarketStructureBar:
    return MarketStructureBar(
        event_time=EVENT_TIME,
        received_at=RECEIVED_AT,
        source_event_id="evt-1",
        open=Decimal("100"),
        high=Decimal("101"),
        low=Decimal("99"),
        close=Decimal("100.5"),
        volume=Decimal("10"),
    )


@pytest.mark.parametrize("field", ["event_time", "received_at"])
def test_bar_rejects_invalid_temporal_runtime_types(field: str) -> None:
    values: dict[str, object] = {
        "event_time": EVENT_TIME,
        "received_at": RECEIVED_AT,
    }
    values[field] = "2026-10-02T13:00:00Z"

    with pytest.raises(ValueError, match=f"{field} must be a datetime"):
        MarketStructureBar(
            event_time=cast(datetime, values["event_time"]),
            received_at=cast(datetime, values["received_at"]),
            source_event_id="evt-1",
            open=Decimal("100"),
            high=Decimal("101"),
            low=Decimal("99"),
            close=Decimal("100.5"),
            volume=Decimal("10"),
        )


@pytest.mark.parametrize("field", ["event_time", "received_at"])
def test_request_rejects_invalid_temporal_runtime_types(field: str) -> None:
    values: dict[str, object] = {
        "event_time": EVENT_TIME,
        "received_at": RECEIVED_AT,
    }
    values[field] = "2026-10-02T13:00:00Z"

    with pytest.raises(ValueError, match=f"{field} must be a datetime"):
        MarketStructureRequest(
            bars=(_bar(),),
            event_time=cast(datetime, values["event_time"]),
            received_at=cast(datetime, values["received_at"]),
            source_event_id="evt-1",
        )


def test_output_rejects_invalid_temporal_runtime_type() -> None:
    with pytest.raises(ValueError, match="event_time must be a datetime"):
        MarketStructureOutput(
            points=(),
            events=(),
            state=None,
            event_time=cast(datetime, "2026-10-02T13:00:00Z"),
            source_event_id="evt-1",
        )
