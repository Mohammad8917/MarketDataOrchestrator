"""Unit tests for deterministic structural swing labeling."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from analysis.structure.swing_detector import ConfirmedSwing
from analysis.structure.swing_labeler import DeterministicStructureLabeler
from shared.contracts.market_structure import MarketStructureBar


def _bar(index: int, high: int, low: int) -> MarketStructureBar:
    timestamp = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=index)
    return MarketStructureBar(
        event_time=timestamp,
        received_at=timestamp,
        source_event_id=f"bar-{index}",
        open=Decimal(str(low + 1)),
        high=Decimal(str(high)),
        low=Decimal(str(low)),
        close=Decimal(str(low + 1)),
        volume=Decimal("1"),
    )


def test_labels_confirmed_highs() -> None:
    swings = (
        ConfirmedSwing("high", 2, _bar(2, 12, 8)),
        ConfirmedSwing("high", 5, _bar(5, 14, 9)),
        ConfirmedSwing("high", 8, _bar(8, 13, 9)),
    )
    points = DeterministicStructureLabeler().label(swings)
    assert [(point.kind, point.price_level) for point in points] == [
        ("HH", Decimal("14")),
        ("LH", Decimal("13")),
    ]


def test_labels_confirmed_lows() -> None:
    swings = (
        ConfirmedSwing("low", 2, _bar(2, 12, 8)),
        ConfirmedSwing("low", 5, _bar(5, 14, 10)),
        ConfirmedSwing("low", 8, _bar(8, 13, 7)),
    )
    points = DeterministicStructureLabeler().label(swings)
    assert [(point.kind, point.price_level) for point in points] == [
        ("HL", Decimal("10")),
        ("LL", Decimal("7")),
    ]


def test_first_swing_has_no_label() -> None:
    assert DeterministicStructureLabeler().label(
        (ConfirmedSwing("high", 2, _bar(2, 12, 8)),)
    ) == ()
