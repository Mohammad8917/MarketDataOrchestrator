"""FILE: regime/classification/regime_labels.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-09-29
DATE_PERSIAN: 1405-07-07
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Define the canonical machine-readable regime classification vocabulary.
LAYER: regime
OWNS: Stable regime label identifiers only.
DOES_NOT_OWN: thresholds, feature construction, classification algorithms, strategy execution, decision finalization, risk, provider I/O
DEPENDENCIES: stdlib:enum
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from enum import StrEnum


class RegimeLabel(StrEnum):
    """Canonical semantic labels emitted by regime classifiers."""

    TREND_UP = "trend_up"
    TREND_DOWN = "trend_down"
    RANGE_LOW_VOLATILITY = "range_low_volatility"
    RANGE_HIGH_VOLATILITY = "range_high_volatility"
    UNKNOWN = "unknown"


CANONICAL_REGIME_LABELS: tuple[RegimeLabel, ...] = tuple(RegimeLabel)
