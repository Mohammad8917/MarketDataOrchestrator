"""Unit tests for deterministic market-structure state classification."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from analysis.structure.state_classifier import DeterministicStructureStateClassifier
from shared.contracts.market_structure import MarketStructureBar


def _bar(index: int, high: int, low: int) -> MarketStructureBar:
    timestamp = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=index)
    return MarketStructureBar(
        event_time=timestamp,
        received_at=timestamp,
        source_event_id=f"bar-{index}",
        open=Decimal(str(low)),
        high=Decimal(str(high)),
        low=Decimal(str(low)),
        close=Decimal(str(low)),
        volume=Decimal("1"),
    )


def test_classifies_expansion_from_equal_length_windows() -> None:
    bars = tuple(
        [_bar(index, 11, 10) for index in range(10)]
        + [_bar(index, 14, 10) for index in range(10, 20)]
    )

    state = DeterministicStructureStateClassifier().classify(bars)

    assert state.kind == "expansion"
    assert state.event_time == bars[-1].event_time
    assert state.source_event_id == bars[-1].source_event_id


def test_classifies_compression_from_equal_length_windows() -> None:
    bars = tuple(
        [_bar(index, 14, 10) for index in range(10)]
        + [_bar(index, 11, 10) for index in range(10, 20)]
    )

    state = DeterministicStructureStateClassifier().classify(bars)

    assert state.kind == "compression"


def test_classifies_range_between_expansion_and_compression_thresholds() -> None:
    bars = tuple(
        [_bar(index, 12, 10) for index in range(10)]
        + [_bar(index, 13, 10) for index in range(10, 20)]
    )

    state = DeterministicStructureStateClassifier().classify(bars)

    assert state.kind == "range"


def test_requires_two_equal_length_windows() -> None:
    bars = tuple(_bar(index, 11, 10) for index in range(19))

    try:
        DeterministicStructureStateClassifier().classify(bars)
    except ValueError as exc:
        assert "insufficient history" in str(exc)
    else:
        raise AssertionError("expected deterministic insufficient-history failure")
