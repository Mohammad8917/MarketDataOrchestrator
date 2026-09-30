from __future__ import annotations

from decimal import Decimal

from analysis.structure.swing_detector import ConfirmedSwing
from shared.contracts.market_structure import (
    MARKET_STRUCTURE_METHODOLOGY,
    MarketStructureBar,
    StructureEvent,
)


class DeterministicStructureBreakDetector:
    """Emit one descriptive break event when price first crosses a confirmed level."""

    def detect(
        self,
        bars: tuple[MarketStructureBar, ...],
        swings: tuple[ConfirmedSwing, ...],
    ) -> tuple[StructureEvent, ...]:
        ordered_swings = tuple(sorted(swings, key=lambda swing: swing.index))
        swing_position = 0
        latest_high: ConfirmedSwing | None = None
        latest_low: ConfirmedSwing | None = None
        broken_high: Decimal | None = None
        broken_low: Decimal | None = None
        previous_close: Decimal | None = None
        events: list[StructureEvent] = []

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
                    broken_high = None
                else:
                    latest_low = swing
                    broken_low = None
                swing_position += 1

            if latest_high is not None:
                level = latest_high.bar.high
                crossed = previous_close is not None and previous_close <= level < bar.close
                if crossed and broken_high != level:
                    events.append(
                        StructureEvent(
                            kind="breakout",
                            event_time=bar.event_time,
                            source_event_id=bar.source_event_id,
                            reference_price=level,
                        )
                    )
                    broken_high = level

            if latest_low is not None:
                level = latest_low.bar.low
                crossed = previous_close is not None and previous_close >= level > bar.close
                if crossed and broken_low != level:
                    events.append(
                        StructureEvent(
                            kind="breakdown",
                            event_time=bar.event_time,
                            source_event_id=bar.source_event_id,
                            reference_price=level,
                        )
                    )
                    broken_low = level

            previous_close = bar.close

        return tuple(events)
"""FILE: analysis/structure/break_detector.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-01
DATE_PERSIAN: 1405-07-09
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Detect deterministic descriptive breakout and breakdown events from confirmed structural levels.
LAYER: analysis
OWNS: Structural break event detection and its local invariants.
DOES_NOT_OWN: strategy decisions, risk, execution, provider I/O, persistence.
DEPENDENCIES: decimal, analysis.structure.swing_detector, shared.contracts.market_structure
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

