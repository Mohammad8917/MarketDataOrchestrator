"""FILE: analysis/structure/break_detector.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-01
DATE_PERSIAN: 1405-07-09
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Detect deterministic breakout and breakdown events from confirmed structural pivots.
LAYER: analysis
OWNS: Descriptive breakout and breakdown event detection only.
DOES_NOT_OWN: pivot detection, structural labeling, structure shift, state classification, strategy, risk, execution, provider I/O
DEPENDENCIES: shared.contracts.market_structure, analysis.structure.swing_detector
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from decimal import Decimal

from analysis.structure.swing_detector import ConfirmedSwing
from shared.contracts.market_structure import (
    MARKET_STRUCTURE_METHODOLOGY,
    MarketStructureBar,
    StructureEvent,
)


class DeterministicStructureBreakDetector:
    """Detect point-in-time breakout and breakdown events."""

    def detect(
        self,
        bars: tuple[MarketStructureBar, ...],
        swings: tuple[ConfirmedSwing, ...],
    ) -> tuple[StructureEvent, ...]:
        latest_high: ConfirmedSwing | None = None
        latest_low: ConfirmedSwing | None = None
        high_activated: Decimal | None = None
        low_activated: Decimal | None = None
        previous_close: Decimal | None = None
        events: list[StructureEvent] = []

        ordered_swings = tuple(sorted(swings, key=lambda swing: swing.index))
        swing_position = 0

        for index, bar in enumerate(bars):
            while (
                swing_position < len(ordered_swings)
                and ordered_swings[swing_position].index
                + MARKET_STRUCTURE_METHODOLOGY.pivot_right_bars
                <= index
            ):
                swing = ordered_swings[swing_position]
                if swing.kind == "high":
                    latest_high = swing
                    high_activated = None
                else:
                    latest_low = swing
                    low_activated = None
                swing_position += 1

            if latest_high is not None:
                level = latest_high.bar.high
                if high_activated != level:
                    if bar.close > level:
                        events.append(
                            StructureEvent(
                                kind="breakout",
                                event_time=bar.event_time,
                                source_event_id=bar.source_event_id,
                                reference_price=level,
                            )
                        )
                        high_activated = level
                elif previous_close is not None and previous_close <= level and bar.close > level:
                    events.append(
                        StructureEvent(
                            kind="breakout",
                            event_time=bar.event_time,
                            source_event_id=bar.source_event_id,
                            reference_price=level,
                        )
                    )

            if latest_low is not None:
                level = latest_low.bar.low
                if low_activated != level:
                    if bar.close < level:
                        events.append(
                            StructureEvent(
                                kind="breakdown",
                                event_time=bar.event_time,
                                source_event_id=bar.source_event_id,
                                reference_price=level,
                            )
                        )
                        low_activated = level
                elif previous_close is not None and previous_close >= level and bar.close < level:
                    events.append(
                        StructureEvent(
                            kind="breakdown",
                            event_time=bar.event_time,
                            source_event_id=bar.source_event_id,
                            reference_price=level,
                        )
                    )

            previous_close = bar.close

        return tuple(events)
