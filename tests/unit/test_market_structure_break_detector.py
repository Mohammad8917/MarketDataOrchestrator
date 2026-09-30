"""Unit tests for deterministic market-structure break detection."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from analysis.structure.break_detector import DeterministicStructureBreakDetector
from analysis.structure.swing_detector import ConfirmedSwing
from shared.contracts.market_structure import MarketStructureBar


def _bar(index: int, high: int, low: int, close: int) -> MarketStructureBar:
    timestamp = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=index)
    return MarketStructureBar(
        event_time=timestamp,
        received_at=timestamp,
        source_event_id=f"bar-{index}",
        open=Decimal(str(close)),
        high=Decimal(str(high)),
        low=Decimal(str(low)),
        close=Decimal(str(close)),
        volume=Decimal("1"),
    )


def test_detects_breakout_above_latest_confirmed_high() -> None:
    bars = (
        _bar(0, 10, 8, 9),
        _bar(1, 11, 8, 10),
        _bar(2, 12, 8, 11),
        _bar(3, 11, 8, 10),
        _bar(4, 10, 8, 9),
        _bar(5, 13, 9, 13),
    )
    swings = (ConfirmedSwing("high", 2, bars[2]),)

    events = DeterministicStructureBreakDetector().detect(bars, swings)

    assert [(event.kind, event.reference_price) for event in events] == [
        ("breakout", Decimal("12")),
    ]


def test_detects_breakdown_below_latest_confirmed_low() -> None:
    bars = (
        _bar(0, 14, 10, 13),
        _bar(1, 13, 9, 12),
        _bar(2, 14, 8, 9),
        _bar(3, 13, 9, 12),
        _bar(4, 14, 10, 13),
        _bar(5, 12, 7, 7),
    )
    swings = (ConfirmedSwing("low", 2, bars[2]),)

    events = DeterministicStructureBreakDetector().detect(bars, swings)

    assert [(event.kind, event.reference_price) for event in events] == [
        ("breakdown", Decimal("8")),
    ]


def test_does_not_emit_break_before_swing_is_confirmed() -> None:
    bars = (
        _bar(0, 10, 8, 9),
        _bar(1, 11, 8, 10),
        _bar(2, 12, 8, 12),
        _bar(3, 13, 9, 13),
    )
    swings = ()

    assert DeterministicStructureBreakDetector().detect(bars, swings) == ()


def test_does_not_repeat_breakout_while_price_remains_above_same_level() -> None:
    bars = (
        _bar(0, 10, 8, 9),
        _bar(1, 11, 8, 10),
        _bar(2, 12, 8, 11),
        _bar(3, 11, 8, 10),
        _bar(4, 10, 8, 9),
        _bar(5, 13, 9, 13),
        _bar(6, 14, 10, 13),
    )
    swings = (ConfirmedSwing("high", 2, bars[2]),)

    events = DeterministicStructureBreakDetector().detect(bars, swings)

    assert len(events) == 1


def test_close_equal_to_level_is_not_a_break() -> None:
    bars = (
        _bar(0, 10, 8, 9),
        _bar(1, 11, 8, 10),
        _bar(2, 12, 8, 11),
        _bar(3, 11, 8, 10),
        _bar(4, 10, 8, 9),
        _bar(5, 12, 9, 12),
    )
    swings = (ConfirmedSwing("high", 2, bars[2]),)

    assert DeterministicStructureBreakDetector().detect(bars, swings) == ()
