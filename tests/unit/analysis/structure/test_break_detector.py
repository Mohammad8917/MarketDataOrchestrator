"""FILE: tests/unit/analysis/structure/test_break_detector.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-01
DATE_PERSIAN: 1405-07-09
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify deterministic market-structure implementation invariants and contract behavior.
LAYER: tests
OWNS: Focused unit or contract acceptance tests for the market-structure subsystem.
DOES_NOT_OWN: production implementation, provider transport, persistence, or trading decisions.
DEPENDENCIES: pytest, analysis.structure.break_detector, analysis.structure.swing_detector, shared.contracts.market_structure
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

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


def test_breakout_requires_crossing_confirmed_high() -> None:
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


def test_breakdown_requires_crossing_confirmed_low() -> None:
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


def test_equal_close_is_not_a_break() -> None:
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


def test_break_is_not_repeated_above_same_level() -> None:
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
    assert len(DeterministicStructureBreakDetector().detect(bars, swings)) == 1
