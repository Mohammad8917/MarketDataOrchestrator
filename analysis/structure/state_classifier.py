"""FILE: analysis/structure/state_classifier.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-01
DATE_PERSIAN: 1405-07-09
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Classify current market-structure state as range, expansion, or compression.
LAYER: analysis
OWNS: Descriptive equal-window structure-state classification only.
DOES_NOT_OWN: swing detection, break detection, structure shift, strategy, risk, execution, provider I/O
DEPENDENCIES: shared.contracts.market_structure
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from decimal import Decimal

from shared.contracts.market_structure import (
    MARKET_STRUCTURE_METHODOLOGY,
    MarketStructureBar,
    StructureState,
)


class DeterministicStructureStateClassifier:
    """Classify the latest equal-length state window against its predecessor."""

    def classify(self, bars: tuple[MarketStructureBar, ...]) -> StructureState:
        lookback = MARKET_STRUCTURE_METHODOLOGY.state_lookback
        required = lookback * 2
        if len(bars) < required:
            raise ValueError("insufficient history for market structure state")

        current = bars[-lookback:]
        previous = bars[-required:-lookback]

        current_high = max(bar.high for bar in current)
        current_low = min(bar.low for bar in current)
        previous_high = max(bar.high for bar in previous)
        previous_low = min(bar.low for bar in previous)

        current_width = current_high - current_low
        previous_width = previous_high - previous_low

        if previous_width == 0:
            kind = "range" if current_width == 0 else "expansion"
        else:
            ratio = current_width / previous_width
            if ratio >= Decimal(str(MARKET_STRUCTURE_METHODOLOGY.expansion_ratio)):
                kind = "expansion"
            elif ratio <= Decimal(str(MARKET_STRUCTURE_METHODOLOGY.compression_ratio)):
                kind = "compression"
            else:
                kind = "range"

        latest = bars[-1]
        return StructureState(
            kind=kind,
            event_time=latest.event_time,
            source_event_id=latest.source_event_id,
        )
