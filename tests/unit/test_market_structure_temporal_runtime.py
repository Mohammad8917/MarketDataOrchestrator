"""Regression coverage for market-structure temporal runtime validation."""

from datetime import UTC, datetime
from decimal import Decimal
from math import inf, nan
from typing import cast

import pytest

from shared.contracts.market_structure import (
    MarketStructureBar,
    MarketStructureMethodology,
    MarketStructureOutput,
    MarketStructureRequest,
    StructureEvent,
    StructurePoint,
    StructureState,
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


@pytest.mark.parametrize("value", ["", "   ", None, 1])
def test_output_rejects_invalid_contract_version(value: object) -> None:
    with pytest.raises(ValueError, match="contract_version must (be a string|not be empty)"):
        MarketStructureOutput(
            points=(),
            events=(),
            state=None,
            event_time=EVENT_TIME,
            source_event_id="evt-1",
            contract_version=value,  # type: ignore[arg-type]
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


@pytest.mark.parametrize("value", ["1.2", True, None, object(), inf, -inf, nan])
def test_methodology_rejects_invalid_expansion_ratio_runtime_types(value: object) -> None:
    with pytest.raises(ValueError, match="expansion_ratio must be (numeric|finite|> 1)"):
        MarketStructureMethodology(expansion_ratio=value)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", ["0.5", True, None, object(), inf, -inf, nan])
def test_methodology_rejects_invalid_compression_ratio_runtime_types(value: object) -> None:
    with pytest.raises(ValueError, match="compression_ratio must be (numeric|finite|between)"):
        MarketStructureMethodology(compression_ratio=value)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [[], {}, None])
def test_structure_point_rejects_unhashable_or_invalid_kind_runtime_types(value: object) -> None:
    with pytest.raises(ValueError, match="kind must be one of HH, HL, LH, LL"):
        StructurePoint(
            kind=value,  # type: ignore[arg-type]
            event_time=EVENT_TIME,
            source_event_id="event-1",
            price_level=Decimal("100"),
        )


@pytest.mark.parametrize("value", [[], {}, None])
def test_structure_event_rejects_unhashable_or_invalid_kind_runtime_types(value: object) -> None:
    with pytest.raises(
        ValueError, match="kind must be one of breakout, breakdown, structure_shift"
    ):
        StructureEvent(
            kind=value,  # type: ignore[arg-type]
            event_time=EVENT_TIME,
            source_event_id="event-1",
            reference_price=Decimal("100"),
        )


@pytest.mark.parametrize("value", [[], {}, None])
def test_structure_state_rejects_unhashable_or_invalid_kind_runtime_types(value: object) -> None:
    with pytest.raises(ValueError, match="kind must be one of range, expansion, compression"):
        StructureState(
            kind=value,  # type: ignore[arg-type]
            event_time=EVENT_TIME,
            source_event_id="event-1",
        )
