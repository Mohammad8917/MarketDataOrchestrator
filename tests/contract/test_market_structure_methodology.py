"""Contract tests for deterministic market-structure methodology."""

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
