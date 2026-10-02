"""Unit tests for the canonical Backtest performance-analysis replay boundary."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from backtest.performance_replay import (
    CONTRACT_ID,
    CONTRACT_VERSION,
    PerformanceAnalysisReplay,
)
from shared.contracts.equity_curve import EquityCurveData


def curve(*values: str) -> EquityCurveData:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    equity = tuple(Decimal(value) for value in values)
    return EquityCurveData(
        timestamps=tuple(start + timedelta(hours=i) for i in range(len(equity))),
        equity=equity,
        drawdown=tuple(Decimal("0") for _ in equity),
    )


def test_performance_replay_returns_immutable_contract_output() -> None:
    output = PerformanceAnalysisReplay().run(curve("100", "120", "90"))

    assert output.contract_version == CONTRACT_VERSION
    assert output.metrics.observations == 3
    assert output.metrics.total_return == Decimal("-0.1")
    assert output.metrics.max_drawdown == Decimal("-0.25")


def test_performance_replay_exposes_canonical_contract_identity() -> None:
    replay = PerformanceAnalysisReplay()

    assert replay.contract_id == CONTRACT_ID
    assert replay.contract_version == CONTRACT_VERSION


def test_performance_replay_rejects_invalid_input() -> None:
    with pytest.raises(TypeError, match="equity_curve must satisfy EquityCurve"):
        PerformanceAnalysisReplay().run(object())  # type: ignore[arg-type]
