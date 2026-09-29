"""FILE: tests/unit/test_strategy_registry.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-29
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify deterministic strategy-name registration and construction.
LAYER: tests
OWNS: StrategyRegistry contract and behavior assertions.
DOES_NOT_OWN: strategy implementation, backtest execution, persistence, provider I/O.
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
"""

import pytest

from strategy.catalog.strategy_registry import StrategyRegistry


def test_register_and_create_strategy() -> None:
    registry = StrategyRegistry()
    factory = lambda period: ("donchian", period)

    registry.register("donchian", factory)

    assert registry.names() == ("donchian",)
    assert registry.create("donchian", period=20) == ("donchian", 20)


def test_names_are_deterministically_sorted() -> None:
    registry = StrategyRegistry()
    registry.register("zeta", lambda period: ("zeta", period))
    registry.register("alpha", lambda period: ("alpha", period))

    assert registry.names() == ("alpha", "zeta")


def test_duplicate_registration_is_rejected() -> None:
    registry = StrategyRegistry()
    registry.register("donchian", lambda period: period)

    with pytest.raises(ValueError, match="already registered"):
        registry.register("donchian", lambda period: period)


def test_unknown_strategy_is_rejected() -> None:
    registry = StrategyRegistry()

    with pytest.raises(KeyError, match="unknown strategy: donchian"):
        registry.create("donchian", period=20)


@pytest.mark.parametrize("name", ["", " ", "Donchian"])
def test_strategy_name_must_be_normalized_identifier(name: str) -> None:
    registry = StrategyRegistry()

    with pytest.raises(ValueError, match="strategy name"):
        registry.register(name, lambda period: period)
