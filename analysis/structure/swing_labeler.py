"""FILE: analysis/structure/swing_labeler.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-01
DATE_PERSIAN: 1405-07-09
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Assign deterministic HH, HL, LH, and LL labels to confirmed market-structure swings.
LAYER: analysis
OWNS: Descriptive structural labeling and its local invariants.
DOES_NOT_OWN: trading decisions, risk, execution, provider I/O, persistence.
DEPENDENCIES: decimal, analysis.structure.swing_detector, shared.contracts.market_structure
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from decimal import Decimal

from analysis.structure.swing_detector import ConfirmedSwing
from shared.contracts.market_structure import StructurePoint


class DeterministicStructureLabeler:
    """Assign descriptive structural vocabulary to confirmed swings."""

    def label(self, swings: tuple[ConfirmedSwing, ...]) -> tuple[StructurePoint, ...]:
        previous_high: Decimal | None = None
        previous_low: Decimal | None = None
        points: list[StructurePoint] = []

        for swing in swings:
            if swing.kind == "high":
                if previous_high is not None:
                    points.append(
                        StructurePoint(
                            kind="HH" if swing.bar.high > previous_high else "LH",
                            event_time=swing.bar.event_time,
                            source_event_id=swing.bar.source_event_id,
                            price_level=swing.bar.high,
                        )
                    )
                previous_high = swing.bar.high
            else:
                if previous_low is not None:
                    points.append(
                        StructurePoint(
                            kind="HL" if swing.bar.low > previous_low else "LL",
                            event_time=swing.bar.event_time,
                            source_event_id=swing.bar.source_event_id,
                            price_level=swing.bar.low,
                        )
                    )
                previous_low = swing.bar.low

        return tuple(points)
