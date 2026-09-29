"""FILE: tests/unit/test_strategy_comparison.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-29
DATE_PERSIAN: 1405-07-07
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify deterministic strategy comparison construction and contract invariants.
LAYER: tests
OWNS: Assertions for strategy comparison behavior.
DOES_NOT_OWN: strategy logic, backtest execution, persistence, or ranking policy.
DEPENDENCIES: datetime, decimal, pytest, shared.contracts.equity_curve, shared.contracts.strategy_comparison, strategy.evaluation.strategy_comparison
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from shared.contracts.equity_curve import EquityCurveData
from shared.contracts.strategy_comparison import StrategyComparisonData
from strategy.evaluation.strategy_comparison import build_strategy_comparison


def make_curve(final: str) -> EquityCurveData:
    timestamps = (
        datetime(2026, 9, 29, 0, tzinfo=timezone.utc),
        datetime(2026, 9, 29, 1, tzinfo=timezone.utc),
    )
    initial = Decimal("100")
    ending = Decimal(final)
    drawdown = min(Decimal("0"), (ending / initial) - Decimal("1"))
    return EquityCurveData(
        timestamps=timestamps,
        equity=(initial, ending),
        drawdown=(Decimal("0"), drawdown),
    )


def test_comparison_orders_entries_by_strategy_name() -> None:
    report = build_strategy_comparison(
        {"zeta": make_curve("90"), "alpha": make_curve("110")}
    )

    assert tuple(name for name, _ in report.entries) == ("alpha", "zeta")
    assert report.entries[0][1].total_return == Decimal("0.1")
    assert report.entries[1][1].total_return == Decimal("-0.1")


def test_comparison_rejects_empty_input() -> None:
    with pytest.raises(ValueError, match="at least one strategy"):
        build_strategy_comparison({})


def test_contract_rejects_duplicate_names() -> None:
    metrics = build_strategy_comparison({"alpha": make_curve("110")}).entries[0][1]

    with pytest.raises(ValueError, match="unique"):
        StrategyComparisonData(entries=(("alpha", metrics), ("alpha", metrics)))


def test_contract_rejects_unsorted_names() -> None:
    metrics = build_strategy_comparison({"alpha": make_curve("110")}).entries[0][1]

    with pytest.raises(ValueError, match="ordered"):
        StrategyComparisonData(entries=(("zeta", metrics), ("alpha", metrics)))
