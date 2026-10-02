"""Unit tests for deterministic next-bar execution semantics."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from backtest.execution_simulator import (
    CloseToCloseExecutionSimulator,
    ExecutionSimulator,
)
from shared.contracts.market_bar import MarketBar


def _bar(minute: int, close: str, *, open_: str | None = None) -> MarketBar:
    value = Decimal(close)
    return MarketBar(
        event_time=datetime(2026, 1, 1, 0, minute, tzinfo=timezone.utc),
        open=Decimal(open_ or close),
        high=value,
        low=value,
        close=value,
        volume=Decimal("1"),
    )


def test_execution_simulator_protocol_conformance() -> None:
    simulator = CloseToCloseExecutionSimulator()
    assert isinstance(simulator, ExecutionSimulator)


def test_flat_position_has_unit_equity_multiplier() -> None:
    simulator = CloseToCloseExecutionSimulator()

    result = simulator.equity_multiplier(
        0,
        _bar(0, "100"),
        _bar(1, "120"),
    )

    assert result == Decimal("1")


def test_long_position_uses_close_to_close_ratio() -> None:
    simulator = CloseToCloseExecutionSimulator()

    result = simulator.equity_multiplier(
        1,
        _bar(0, "100"),
        _bar(1, "125"),
    )

    assert result == Decimal("1.25")


def test_execution_is_exact_decimal_arithmetic() -> None:
    simulator = CloseToCloseExecutionSimulator()

    result = simulator.equity_multiplier(
        1,
        _bar(0, "3"),
        _bar(1, "4"),
    )

    assert result == Decimal("4") / Decimal("3")


@pytest.mark.parametrize("position", [2, -1, True, False])
def test_position_must_be_exactly_zero_or_one(position: object) -> None:
    simulator = CloseToCloseExecutionSimulator()

    with pytest.raises((TypeError, ValueError)):
        simulator.equity_multiplier(
            position,  # type: ignore[arg-type]
            _bar(0, "100"),
            _bar(1, "120"),
        )


def test_bars_must_be_market_bar_instances() -> None:
    simulator = CloseToCloseExecutionSimulator()

    with pytest.raises(TypeError):
        simulator.equity_multiplier(1, object(), _bar(1, "120"))  # type: ignore[arg-type]


def test_current_bar_must_be_strictly_later() -> None:
    simulator = CloseToCloseExecutionSimulator()

    with pytest.raises(ValueError):
        simulator.equity_multiplier(
            1,
            _bar(1, "100"),
            _bar(1, "120"),
        )


def test_zero_previous_close_is_rejected_by_market_bar_contract() -> None:
    with pytest.raises(ValueError):
        MarketBar(
            event_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
            open=Decimal("0"),
            high=Decimal("1"),
            low=Decimal("0"),
            close=Decimal("1"),
            volume=Decimal("1"),
        )


@pytest.mark.parametrize("event_time", ["2026-01-01T00:00:00Z", 0, None])
def test_market_bar_rejects_invalid_event_time_runtime_types(event_time: object) -> None:
    with pytest.raises(ValueError, match="event_time must be a datetime"):
        MarketBar(
            event_time=event_time,  # type: ignore[arg-type]
            open=Decimal("100"),
            high=Decimal("101"),
            low=Decimal("99"),
            close=Decimal("100"),
            volume=Decimal("1"),
        )
