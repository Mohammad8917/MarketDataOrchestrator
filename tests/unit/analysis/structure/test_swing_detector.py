"""FILE: tests/unit/analysis/structure/test_swing_detector.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-01
DATE_PERSIAN: 1405-07-09
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify deterministic market-structure implementation invariants and contract behavior.
LAYER: tests
OWNS: Focused unit or contract acceptance tests for the market-structure subsystem.
DOES_NOT_OWN: production implementation, provider transport, persistence, or trading decisions.
DEPENDENCIES: pytest, analysis.structure.swing_detector, shared.contracts.market_structure
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from analysis.structure.swing_detector import DeterministicSwingDetector
from shared.contracts.market_structure import MarketStructureBar


def _bars(highs: list[int], lows: list[int]) -> tuple[MarketStructureBar, ...]:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return tuple(
        MarketStructureBar(
            event_time=start + timedelta(minutes=index),
            received_at=start + timedelta(minutes=index),
            source_event_id=f"bar-{index}",
            open=Decimal(str((high + low) / 2)),
            high=Decimal(str(high)),
            low=Decimal(str(low)),
            close=Decimal(str((high + low) / 2)),
            volume=Decimal("1"),
        )
        for index, (high, low) in enumerate(zip(highs, lows))
    )


def test_detects_only_confirmed_strict_pivots() -> None:
    bars = _bars([10, 11, 12, 11, 10, 11, 13], [8, 7, 6, 7, 8, 7, 5])
    swings = DeterministicSwingDetector().detect(bars)
    assert [(s.kind, s.index) for s in swings] == [("high", 2), ("low", 2)]


def test_equal_neighbour_disqualifies_matching_pivot_kind() -> None:
    bars = _bars([10, 11, 12, 12, 10, 11], [8, 7, 6, 7, 8, 9])
    swings = DeterministicSwingDetector().detect(bars)
    assert not any(s.kind == "high" and s.index == 2 for s in swings)
    assert any(s.kind == "low" and s.index == 2 for s in swings)


def test_unconfirmed_right_window_is_not_used_as_a_pivot() -> None:
    bars = _bars([10, 11, 12, 11, 10], [8, 7, 6, 7, 8])
    swings = DeterministicSwingDetector().detect(bars)
    assert all(s.index < len(bars) - 2 for s in swings)


def test_insufficient_history_fails_deterministically() -> None:
    bars = _bars([10, 11, 12, 11], [8, 7, 6, 7])
    with pytest.raises(ValueError, match="insufficient history"):
        DeterministicSwingDetector().detect(bars)
