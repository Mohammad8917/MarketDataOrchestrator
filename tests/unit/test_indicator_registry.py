"""FILE: tests/unit/test_indicator_registry.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify indicator registry name resolution and concrete implementation lookup.
LAYER: tests
OWNS: Unit coverage for IndicatorRegistry behavior.
DOES_NOT_OWN: indicator algorithm correctness, strategy execution, provider I/O, release approval
DEPENDENCIES: indicators.core.registry; indicators.trend.ema; pytest
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

import pytest

from indicators.core.registry import IndicatorRegistry
from indicators.trend.ema import ExponentialMovingAverage


def test_registry_resolves_ema_by_name() -> None:
    indicator = IndicatorRegistry().get("EMA", 3)
    assert isinstance(indicator, ExponentialMovingAverage)
    assert indicator.period == 3


def test_registry_normalizes_names() -> None:
    indicator = IndicatorRegistry().get(" ema ", 2)
    assert isinstance(indicator, ExponentialMovingAverage)


def test_registry_rejects_unknown_indicator() -> None:
    with pytest.raises(KeyError, match="^'unknown indicator: UNKNOWN'$"):
        IndicatorRegistry().get("UNKNOWN", 3)
