"""FILE: tests/contract/test_market_structure_methodology.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-01
DATE_PERSIAN: 1405-07-09
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify deterministic market-structure implementation invariants and contract behavior.
LAYER: tests
OWNS: Focused unit or contract acceptance tests for the market-structure subsystem.
DOES_NOT_OWN: production implementation, provider transport, persistence, or trading decisions.
DEPENDENCIES: pytest, shared.contracts.market_structure
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from dataclasses import FrozenInstanceError

import pytest

from shared.contracts.market_structure import (
    MARKET_STRUCTURE_METHODOLOGY_ID,
    MARKET_STRUCTURE_METHODOLOGY_VERSION,
    MarketStructureMethodology,
)

def test_methodology_identity_and_defaults() -> None:
    methodology = MarketStructureMethodology()
    assert MARKET_STRUCTURE_METHODOLOGY_ID == "deterministic_confirmed_pivot_structure"
    assert MARKET_STRUCTURE_METHODOLOGY_VERSION == "1.0.0"
    assert methodology.pivot_left_bars == 2
    assert methodology.pivot_right_bars == 2
    assert methodology.state_lookback == 10
    assert methodology.expansion_ratio == 1.25
    assert methodology.compression_ratio == 0.75

@pytest.mark.parametrize("value", [0, -1, True, 1.5])
def test_pivot_parameters_are_positive_integers(value: object) -> None:
    with pytest.raises(ValueError):
        MarketStructureMethodology(pivot_left_bars=value)  # type: ignore[arg-type]

@pytest.mark.parametrize("value", [1.0, 0.99, 0.0])
def test_expansion_ratio_requires_value_above_one(value: float) -> None:
    with pytest.raises(ValueError, match="expansion_ratio"):
        MarketStructureMethodology(expansion_ratio=value)

@pytest.mark.parametrize("value", [0.0, 1.0, 1.01, -0.1])
def test_compression_ratio_is_open_unit_interval(value: float) -> None:
    with pytest.raises(ValueError, match="compression_ratio"):
        MarketStructureMethodology(compression_ratio=value)

def test_methodology_is_immutable() -> None:
    methodology = MarketStructureMethodology()
    with pytest.raises(FrozenInstanceError):
        methodology.pivot_left_bars = 3  # type: ignore[misc]

