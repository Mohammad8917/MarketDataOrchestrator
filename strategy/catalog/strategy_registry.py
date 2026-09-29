"""FILE: strategy/catalog/strategy_registry.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-29
DATE_PERSIAN: 1405-07-07
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Provide deterministic name-to-factory registration for executable strategies.
LAYER: strategy
OWNS: Strategy name validation, registration uniqueness, deterministic discovery, and construction dispatch.
DOES_NOT_OWN: strategy implementation, backtest execution, persistence, provider I/O, or performance metrics.
DEPENDENCIES: collections.abc, typing
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeAlias

StrategyFactory: TypeAlias = Callable[[int], object]


class StrategyRegistry:
    """Deterministic registry mapping strategy names to construction factories."""

    def __init__(self) -> None:
        self._factories: dict[str, StrategyFactory] = {}

    def register(self, name: str, factory: StrategyFactory) -> None:
        if not isinstance(name, str) or name.strip() != name or not name:
            raise ValueError("strategy name must be a non-empty trimmed string")
        if not name.isidentifier() or name != name.lower():
            raise ValueError("strategy name must be a lowercase identifier")
        if not callable(factory):
            raise TypeError("strategy factory must be callable")
        if name in self._factories:
            raise ValueError(f"strategy already registered: {name}")
        self._factories[name] = factory

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._factories))

    def create(self, name: str, *, period: int) -> object:
        try:
            factory = self._factories[name]
        except KeyError as exc:
            raise KeyError(f"unknown strategy: {name}") from exc
        return factory(period)
