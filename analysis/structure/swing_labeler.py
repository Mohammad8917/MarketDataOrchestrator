"""Deterministic HH/HL/LH/LL structural swing labeling."""

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
