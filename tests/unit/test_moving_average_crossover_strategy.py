"""FILE: tests/unit/test_moving_average_crossover_strategy.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-10-03
DATE_PERSIAN: 1405-07-11
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify deterministic moving-average crossover positions over historical MarketBar values.
LAYER: tests
OWNS: Verification of the moving_average_crossover_strategy test contract and behavior.
DOES_NOT_OWN: Production implementation, runtime orchestration, or release approval.
DEPENDENCIES: shared.contracts.market_bar; strategy.trend.moving_average_crossover; pytest
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from shared.contracts.market_bar import MarketBar
from strategy.trend.moving_average_crossover import (
    MovingAverageCrossoverPosition,
    MovingAverageCrossoverStrategy,
)


def make_bar(index: int, close: int) -> MarketBar:
    value = Decimal(str(close))
    return MarketBar(
        event_time=datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=index),
        open=value,
        high=value,
        low=value,
        close=value,
        volume=Decimal("1"),
    )


def test_periods_must_be_positive_and_ordered() -> None:
    with pytest.raises(ValueError, match="fast period must be positive"):
        MovingAverageCrossoverStrategy(fast_period=0, slow_period=5)
    with pytest.raises(ValueError, match="slow period must be positive"):
        MovingAverageCrossoverStrategy(fast_period=2, slow_period=0)
    with pytest.raises(ValueError, match="fast period must be less than slow period"):
        MovingAverageCrossoverStrategy(fast_period=5, slow_period=5)


@pytest.mark.parametrize("events", [[], None, "events"])
def test_events_reject_non_tuple_runtime_types(events: object) -> None:
    with pytest.raises(ValueError, match="events must be a tuple"):
        MovingAverageCrossoverStrategy(fast_period=2, slow_period=4).signals(events)  # type: ignore[arg-type]


def test_events_reject_invalid_runtime_elements() -> None:
    with pytest.raises(ValueError, match="events must contain only MarketBar values"):
        MovingAverageCrossoverStrategy(fast_period=2, slow_period=4).signals(
            (make_bar(0, 10), object())  # type: ignore[arg-type]
        )


def test_warmup_is_flat_until_slow_period_is_available() -> None:
    events = tuple(make_bar(i, value) for i, value in enumerate((10, 11, 12, 13)))
    assert MovingAverageCrossoverStrategy(fast_period=2, slow_period=4).signals(events) == (
        MovingAverageCrossoverPosition.FLAT,
        MovingAverageCrossoverPosition.FLAT,
        MovingAverageCrossoverPosition.FLAT,
        MovingAverageCrossoverPosition.LONG,
    )


def test_enters_long_when_fast_average_moves_above_slow_average() -> None:
    events = tuple(make_bar(i, value) for i, value in enumerate((10, 10, 10, 20, 20)))
    signals = MovingAverageCrossoverStrategy(fast_period=2, slow_period=4).signals(events)
    assert signals[-1] is MovingAverageCrossoverPosition.LONG


def test_exits_long_when_fast_average_moves_back_below_slow_average() -> None:
    events = tuple(make_bar(i, value) for i, value in enumerate((10, 10, 10, 20, 20, 5, 5)))
    signals = MovingAverageCrossoverStrategy(fast_period=2, slow_period=4).signals(events)
    assert signals[-1] is MovingAverageCrossoverPosition.FLAT


def test_equal_averages_are_flat() -> None:
    events = tuple(make_bar(i, 10) for i in range(4))
    assert MovingAverageCrossoverStrategy(fast_period=2, slow_period=4).signals(events)[-1] is (
        MovingAverageCrossoverPosition.FLAT
    )


def test_order_must_be_strict() -> None:
    events = (make_bar(1, 10), make_bar(1, 11))
    with pytest.raises(ValueError, match="strictly ordered"):
        MovingAverageCrossoverStrategy(fast_period=2, slow_period=4).signals(events)
