"""FILE: tests/contract/test_regime_labels.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-29
DATE_PERSIAN: 1405-07-07
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify the canonical regime semantic label vocabulary.
LAYER: tests
OWNS: Regime label contract verification.
DOES_NOT_OWN: classifier algorithms, strategy execution, risk
DEPENDENCIES: regime.classification.regime_labels
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from regime.classification.regime_labels import CANONICAL_REGIME_LABELS, RegimeLabel


def test_canonical_regime_labels_are_unique_and_stable() -> None:
    assert len(CANONICAL_REGIME_LABELS) == 5
    assert len({label.value for label in CANONICAL_REGIME_LABELS}) == 5
    assert CANONICAL_REGIME_LABELS == (
        RegimeLabel.TREND_UP,
        RegimeLabel.TREND_DOWN,
        RegimeLabel.RANGE_LOW_VOLATILITY,
        RegimeLabel.RANGE_HIGH_VOLATILITY,
        RegimeLabel.UNKNOWN,
    )


def test_labels_are_string_compatible_for_existing_boundary() -> None:
    assert RegimeLabel.TREND_UP == "trend_up"
    assert str(RegimeLabel.UNKNOWN) == "unknown"
