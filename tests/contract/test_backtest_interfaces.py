"""FILE: tests/contract/test_backtest_interfaces.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-25
DATE_PERSIAN: 1405-07-03
RESPONSIBILITY: Verify the typed terminal output and BacktestEngine interface contracts.
LAYER: tests
OWNS: Interface contract shape assertions.
DOES_NOT_OWN: BacktestEngine execution, EquityCurve implementation, runtime behavior
DEPENDENCIES: typing, domain.market_data_event, shared.contracts.equity_curve, backtest.engine
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import get_type_hints

from backtest.engine import BacktestEngine
from domain.market_data_event import MarketDataEvent
from shared.contracts.equity_curve import EquityCurve


def test_equity_curve_is_interface_only() -> None:
    assert getattr(EquityCurve, "_is_protocol", False) is True
    assert (
        get_type_hints(getattr(EquityCurve.timestamps, "fget"))["return"]
        == tuple[datetime, ...]
    )
    assert (
        get_type_hints(getattr(EquityCurve.equity, "fget"))["return"]
        == tuple[Decimal, ...]
    )
    assert (
        get_type_hints(getattr(EquityCurve.drawdown, "fget"))["return"]
        == tuple[Decimal, ...]
    )


def test_backtest_engine_run_signature_is_typed() -> None:
    assert getattr(BacktestEngine, "_is_protocol", False) is True
    hints = get_type_hints(BacktestEngine.run)
    assert hints["events"] == tuple[MarketDataEvent, ...]
    assert hints["return"] is EquityCurve


@dataclass(frozen=True)
class _EquityCurveFake:
    """Test-only implementation used to execute EquityCurve invariants."""

    timestamps: tuple[datetime, ...]
    equity: tuple[Decimal, ...]
    drawdown: tuple[Decimal, ...]

    def __post_init__(self) -> None:
        if not (len(self.timestamps) == len(self.equity) == len(self.drawdown)):
            raise ValueError("EquityCurve sequences must have equal lengths")
        if any(
            ts.tzinfo is None or ts.utcoffset() != timezone.utc.utcoffset(ts)
            for ts in self.timestamps
        ):
            raise ValueError("EquityCurve timestamps must be timezone-aware UTC datetimes")
        if any(curr < prev for prev, curr in zip(self.timestamps, self.timestamps[1:])):
            raise ValueError("EquityCurve timestamps must be non-decreasing")
        if any(not value.is_finite() for value in self.equity):
            raise ValueError("EquityCurve equity values must be finite")
        if any(not value.is_finite() or value > 0 for value in self.drawdown):
            raise ValueError("EquityCurve drawdown values must be finite and non-positive")

    def __len__(self) -> int:
        return len(self.timestamps)

    def __iter__(self):
        return iter(zip(self.timestamps, self.equity, self.drawdown))


def test_equity_curve_invariants_are_executable() -> None:
    ts = (datetime(2026, 1, 1, tzinfo=timezone.utc), datetime(2026, 1, 2, tzinfo=timezone.utc))
    curve = _EquityCurveFake(
        ts, (Decimal("100"), Decimal("95.5")), (Decimal("0"), Decimal("-0.045"))
    )
    assert isinstance(curve, EquityCurve)


def test_equity_curve_rejects_misaligned_sequences() -> None:
    ts = (datetime(2026, 1, 1, tzinfo=timezone.utc),)
    try:
        _EquityCurveFake(ts, (Decimal("100"), Decimal("101")), (Decimal("0"),))
    except ValueError as exc:
        assert "equal lengths" in str(exc)
    else:
        raise AssertionError("misaligned EquityCurve sequences must be rejected")


def test_equity_curve_rejects_non_utc_or_non_monotonic_timestamps() -> None:
    utc = timezone.utc
    try:
        _EquityCurveFake(
            (datetime(2026, 1, 2, tzinfo=utc), datetime(2026, 1, 1, tzinfo=utc)),
            (Decimal("100"), Decimal("101")),
            (Decimal("0"), Decimal("0")),
        )
    except ValueError as exc:
        assert "non-decreasing" in str(exc)
    else:
        raise AssertionError("non-monotonic timestamps must be rejected")

    non_utc = timezone(timedelta(hours=3))
    try:
        _EquityCurveFake(
            (datetime(2026, 1, 1, tzinfo=non_utc),),
            (Decimal("100"),),
            (Decimal("0"),),
        )
    except ValueError as exc:
        assert "UTC" in str(exc)
    else:
        raise AssertionError("non-UTC timestamps must be rejected")


def test_equity_curve_rejects_non_finite_equity_and_positive_drawdown() -> None:
    ts = (datetime(2026, 1, 1, tzinfo=timezone.utc),)
    for equity in (Decimal("NaN"), Decimal("Infinity")):
        try:
            _EquityCurveFake(ts, (equity,), (Decimal("0"),))
        except ValueError as exc:
            assert "finite" in str(exc)
        else:
            raise AssertionError("non-finite equity must be rejected")

    try:
        _EquityCurveFake(ts, (Decimal("100"),), (Decimal("0.01"),))
    except ValueError as exc:
        assert "non-positive" in str(exc)
    else:
        raise AssertionError("positive drawdown must be rejected")
