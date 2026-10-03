"""FILE: shared/contracts/strategy_comparison.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-29
DATE_PERSIAN: 1405-07-07
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Define an immutable deterministic comparison report for multiple strategy performance results.
LAYER: shared
OWNS: Strategy comparison entry identity, deterministic ordering, and value invariants.
DOES_NOT_OWN: strategy selection, backtest execution, metric calculation, persistence, or ranking policy.
DEPENDENCIES: dataclasses, shared.contracts.performance_metrics, typing
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from shared.contracts.performance_metrics import PerformanceMetrics


@runtime_checkable
class StrategyComparison(Protocol):
    """Terminal deterministic collection of named strategy metrics."""

    @property
    def entries(self) -> tuple[tuple[str, PerformanceMetrics], ...]: ...


@dataclass(frozen=True, slots=True)
class StrategyComparisonData:
    """Immutable ordered strategy comparison report."""

    entries: tuple[tuple[str, PerformanceMetrics], ...]

    def __post_init__(self) -> None:
        if not isinstance(self.entries, tuple):
            raise ValueError("entries must be a tuple")

        validated_entries: list[tuple[str, PerformanceMetrics]] = []
        for entry in self.entries:
            if not isinstance(entry, tuple) or len(entry) != 2:
                raise ValueError("strategy entries must be 2-tuples")
            name, metrics = entry
            if not isinstance(name, str) or not name.strip():
                raise ValueError("strategy name must be a non-empty string")
            if not isinstance(metrics, PerformanceMetrics):
                raise TypeError("strategy metrics must satisfy PerformanceMetrics")
            validated_entries.append((name, metrics))

        names = [name for name, _ in validated_entries]
        if names != sorted(names):
            raise ValueError("strategy entries must be ordered by name")
        if len(names) != len(set(names)):
            raise ValueError("strategy names must be unique")
