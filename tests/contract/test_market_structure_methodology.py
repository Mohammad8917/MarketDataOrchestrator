"""FILE: tests/contract/test_market_structure_methodology.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-30
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify the deterministic market-structure methodology contract without implementing detection.
LAYER: tests
OWNS: methodology identity, parameter invariants, and normative rule inventory.
DOES_NOT_OWN: structure calculation, strategy, decision, risk, provider behavior.
DEPENDENCIES: pytest; shared.contracts.market_structure_methodology
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from dataclasses import FrozenInstanceError\nfrom typing import cast

import pytest

from shared.contracts.market_structure_methodology import (
    MARKET_STRUCTURE_METHODOLOGY_CONTRACT_ID,
    MARKET_STRUCTURE_METHODOLOGY_CONTRACT_VERSION,
    MARKET_STRUCTURE_METHODOLOGY_ID,
    MARKET_STRUCTURE_METHODOLOGY_VERSION,
    MarketStructureMethodology,
    methodology_rules,
)


def test_identity() -> None:
    assert MARKET_STRUCTURE_METHODOLOGY_CONTRACT_ID == "market_structure_methodology"
    assert MARKET_STRUCTURE_METHODOLOGY_CONTRACT_VERSION == "1.0.0"
    assert MARKET_STRUCTURE_METHODOLOGY_ID == "deterministic_confirmed_pivot_structure"
    assert MARKET_STRUCTURE_METHODOLOGY_VERSION == "1.0.0"


def test_default_baseline_is_explicit() -> None:
    methodology = MarketStructureMethodology()
    assert methodology.pivot_left_bars == 2
    assert methodology.pivot_right_bars == 2
    assert methodology.state_lookback == 10
    assert methodology.expansion_ratio == 1.25
    assert methodology.compression_ratio == 0.75


@pytest.mark.parametrize(
    "field",
    ["pivot_left_bars", "pivot_right_bars", "state_lookback"],
)
@pytest.mark.parametrize("value", [0, -1, True, 1.5])
def test_bar_parameters_are_positive_integers(field: str, value: object) -> None:
    with pytest.raises(ValueError):
        MarketStructureMethodology(**cast(dict[str, int], {field: value}))


@pytest.mark.parametrize("value", [1.0, 0.99, 0.0, -1.0])
def test_expansion_ratio_requires_value_above_one(value: float) -> None:
    with pytest.raises(ValueError, match="expansion_ratio"):
        MarketStructureMethodology(expansion_ratio=value)


@pytest.mark.parametrize("value", [0.0, 1.0, 1.01, -0.1])
def test_compression_ratio_requires_open_unit_interval(value: float) -> None:
    with pytest.raises(ValueError, match="compression_ratio"):
        MarketStructureMethodology(compression_ratio=value)


def test_methodology_is_immutable() -> None:
    methodology = MarketStructureMethodology()
    with pytest.raises(FrozenInstanceError):
        methodology.pivot_left_bars = 3  # type: ignore[misc]


def test_normative_rules_cover_all_required_outputs() -> None:
    rules = " ".join(methodology_rules()).lower()
    for required in (
        "swing high",
        "swing low",
        "hh",
        "hl",
        "lh",
        "ll",
        "breakout",
        "breakdown",
        "structure shift",
        "range",
        "expansion",
        "compression",
        "future observations never participate",
    ):
        assert required in rules


def test_methodology_is_explicitly_non_trading_and_three_market() -> None:
    rules = " ".join(methodology_rules()).lower()
    for forbidden_action in ("buy", "sell", "order", "position", "sizing", "risk"):
        assert forbidden_action in rules
    assert "crypto" in rules
    assert "forex" in rules
    assert "gold" in rules
