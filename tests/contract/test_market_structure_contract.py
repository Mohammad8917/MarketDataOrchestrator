"""FILE: tests/contract/test_market_structure_contract.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-30
DATE_PERSIAN: 1405-07-08
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify the canonical market-structure contract invariants without defining detection methodology.
LAYER: tests
OWNS: Market-structure contract behavior and market-agnostic boundary tests.
DOES_NOT_OWN: structure detection implementation, trading decisions, risk controls, or provider behavior
DEPENDENCIES: dataclasses, datetime, decimal, pytest, shared.contracts.market_structure
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from dataclasses import fields
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import cast

import pytest

from shared.contracts.market_structure import (
    MARKET_STRUCTURE_CONTRACT_ID,
    MARKET_STRUCTURE_CONTRACT_VERSION,
    MarketStructureBar,
    MarketStructureOutput,
    MarketStructureRequest,
    StructureEvent,
    StructurePoint,
    StructureState,
    StructurePointKind,
    StructureEventKind,
    StructureStateKind,
)


NOW = datetime(2026, 9, 30, 12, tzinfo=UTC)


def bar(index: int) -> MarketStructureBar:
    moment = NOW + timedelta(minutes=index)
    return MarketStructureBar(
        event_time=moment,
        received_at=moment,
        source_event_id=f"evt-{index}",
        open=Decimal("100"),
        high=Decimal("105"),
        low=Decimal("95"),
        close=Decimal("102"),
        volume=Decimal("10"),
    )


def request(count: int = 3) -> MarketStructureRequest:
    bars = tuple(bar(index) for index in range(count))
    return MarketStructureRequest(
        bars=bars,
        event_time=bars[-1].event_time,
        received_at=bars[-1].received_at,
        source_event_id=bars[-1].source_event_id,
    )


def test_contract_identity() -> None:
    assert MARKET_STRUCTURE_CONTRACT_ID == "market_structure_boundary"
    assert MARKET_STRUCTURE_CONTRACT_VERSION == "1.0.0"


def test_request_is_point_in_time_and_strictly_ordered() -> None:
    valid = request()
    assert valid.bars[-1].event_time == valid.event_time

    future = bar(4)
    with pytest.raises(ValueError, match="after event_time"):
        MarketStructureRequest(
            bars=(*valid.bars, future),
            event_time=valid.event_time,
            received_at=valid.received_at,
            source_event_id=valid.source_event_id,
        )

    with pytest.raises(ValueError, match="strictly ordered"):
        MarketStructureRequest(
            bars=(valid.bars[0], valid.bars[2], valid.bars[1]),
            event_time=valid.event_time,
            received_at=valid.received_at,
            source_event_id=valid.source_event_id,
        )


@pytest.mark.parametrize(
    ("kind", "expected"),
    [("HH", "HH"), ("HL", "HL"), ("LH", "LH"), ("LL", "LL")],
)
def test_structural_point_vocabulary(kind: str, expected: str) -> None:
    point = StructurePoint(cast(StructurePointKind, kind), NOW, "evt-1", Decimal("100"))
    assert point.kind == expected


@pytest.mark.parametrize(
    "kind",
    ["BUY", "SELL", "bullish", "bearish", "invalid"],
)
def test_structural_point_rejects_trading_or_unknown_labels(kind: str) -> None:
    with pytest.raises(ValueError, match="kind"):
        StructurePoint(cast(StructurePointKind, kind), NOW, "evt-1", Decimal("100"))


@pytest.mark.parametrize(
    "kind",
    ["breakout", "breakdown", "structure_shift"],
)
def test_structural_event_vocabulary(kind: str) -> None:
    event = StructureEvent(cast(StructureEventKind, kind), NOW, "evt-1", Decimal("100"))
    assert event.kind == kind


@pytest.mark.parametrize("kind", ["range", "expansion", "compression"])
def test_structural_state_vocabulary(kind: str) -> None:
    state = StructureState(cast(StructureStateKind, kind), NOW, "evt-1")
    assert state.kind == kind


@pytest.mark.parametrize("version", ["2.0.0", "0.9.0", "unknown"])
def test_output_rejects_unsupported_contract_version(version: str) -> None:
    with pytest.raises(ValueError, match="unsupported contract_version"):
        MarketStructureOutput(
            points=(),
            events=(),
            state=None,
            event_time=NOW,
            source_event_id="evt-1",
            contract_version=version,
        )


def test_output_has_no_trade_action_semantics() -> None:
    output = MarketStructureOutput((), (), None, NOW, "evt-1")
    field_names = {field.name for field in fields(output)}
    assert "action" not in field_names
    assert "side" not in field_names
    assert "buy" not in field_names
    assert "sell" not in field_names


def test_contract_is_market_agnostic() -> None:
    field_names = {
        field.name
        for contract_type in (
            MarketStructureBar,
            MarketStructureRequest,
            MarketStructureOutput,
        )
        for field in fields(contract_type)
    }
    forbidden_provider_assumptions = {
        "exchange",
        "funding_rate",
        "order_book",
        "futures",
        "provider",
        "symbol",
    }
    assert field_names.isdisjoint(forbidden_provider_assumptions)


def test_ohlcv_invariants_are_enforced() -> None:
    with pytest.raises(ValueError, match="high"):
        MarketStructureBar(
            event_time=NOW,
            received_at=NOW,
            source_event_id="evt-1",
            open=Decimal("100"),
            high=Decimal("99"),
            low=Decimal("95"),
            close=Decimal("98"),
            volume=Decimal("10"),
        )

    with pytest.raises(ValueError, match="non-negative"):
        MarketStructureBar(
            event_time=NOW,
            received_at=NOW,
            source_event_id="evt-1",
            open=Decimal("100"),
            high=Decimal("105"),
            low=Decimal("95"),
            close=Decimal("102"),
            volume=Decimal("-1"),
        )


def test_output_rejects_non_tuple_points_and_events() -> None:
    with pytest.raises(ValueError, match="points must be a tuple"):
        MarketStructureOutput([], (), None, NOW, "evt-1")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="events must be a tuple"):
        MarketStructureOutput((), [], None, NOW, "evt-1")  # type: ignore[arg-type]


def test_output_rejects_malformed_nested_values() -> None:
    with pytest.raises(ValueError, match="points must contain only"):
        MarketStructureOutput((object(),), (), None, NOW, "evt-1")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="events must contain only"):
        MarketStructureOutput((), (object(),), None, NOW, "evt-1")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="state must be a StructureState"):
        MarketStructureOutput((), (), object(), NOW, "evt-1")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("event_time", "2026-09-30T12:00:00Z"),
        ("received_at", "2026-09-30T12:00:00Z"),
        ("source_event_id", ""),
        ("source_event_id", "   "),
    ],
)
def test_bar_rejects_invalid_boundary_values(field: str, value: object) -> None:
    values = {
        "event_time": NOW,
        "received_at": NOW,
        "source_event_id": "evt-1",
        "open": Decimal("100"),
        "high": Decimal("105"),
        "low": Decimal("95"),
        "close": Decimal("102"),
        "volume": Decimal("10"),
    }
    values[field] = value
    message = (
        f"{field} must be a datetime"
        if field in {"event_time", "received_at"}
        else f"{field} must not be empty"
    )
    with pytest.raises(ValueError, match=message):
        MarketStructureBar(**values)  # type: ignore[arg-type]


def test_request_rejects_empty_bars() -> None:
    with pytest.raises(ValueError, match="bars must not be empty"):
        MarketStructureRequest((), NOW, NOW, "evt-1")


def test_request_rejects_malformed_bar_values() -> None:
    with pytest.raises(ValueError, match="bars must contain only MarketStructureBar"):
        MarketStructureRequest((object(),), NOW, NOW, "evt-1")  # type: ignore[arg-type]


def test_request_rejects_temporal_mismatch() -> None:
    with pytest.raises(ValueError, match="received_at cannot precede event_time"):
        MarketStructureRequest((bar(0),), NOW, NOW - timedelta(minutes=1), "evt-1")


def test_output_rejects_invalid_event_time_and_source_id() -> None:
    with pytest.raises(ValueError, match="event_time must be a datetime"):
        MarketStructureOutput((), (), None, "invalid", "evt-1")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="source_event_id must not be empty"):
        MarketStructureOutput((), (), None, NOW, "   ")


def test_output_rejects_invalid_nested_state_type() -> None:
    with pytest.raises(ValueError, match="state must be a StructureState"):
        MarketStructureOutput((), (), object(), NOW, "evt-1")  # type: ignore[arg-type]
