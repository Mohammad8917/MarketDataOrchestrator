from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from shared.contracts.equity_curve import EquityCurve, EquityCurveData


def ts(day: int) -> datetime:
    return datetime(2026, 1, day, tzinfo=timezone.utc)


def test_equity_curve_data_is_runtime_equity_curve() -> None:
    curve = EquityCurveData(
        timestamps=(ts(1), ts(2)),
        equity=(Decimal("100"), Decimal("95")),
        drawdown=(Decimal("0"), Decimal("-0.05")),
    )
    assert isinstance(curve, EquityCurve)
    assert len(curve) == 2
    assert tuple(curve) == (Decimal("100"), Decimal("95"))


@pytest.mark.parametrize(
    ("timestamps", "equity", "drawdown"),
    [
        ((ts(1),), (Decimal("100"), Decimal("101")), (Decimal("0"),)),
        ((ts(1),), (Decimal("100"),), (Decimal("0"), Decimal("-0.01"))),
    ],
)
def test_rejects_misaligned_series(
    timestamps: tuple[datetime, ...],
    equity: tuple[Decimal, ...],
    drawdown: tuple[Decimal, ...],
) -> None:
    with pytest.raises(ValueError, match="equal length"):
        EquityCurveData(timestamps, equity, drawdown)


def test_rejects_naive_and_non_utc_timestamps() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        EquityCurveData((datetime(2026, 1, 1),), (Decimal("100"),), (Decimal("0"),))

    non_utc = timezone(timedelta(hours=3))
    with pytest.raises(ValueError, match="UTC"):
        EquityCurveData(
            (datetime(2026, 1, 1, tzinfo=non_utc),),
            (Decimal("100"),),
            (Decimal("0"),),
        )


@pytest.mark.parametrize(
    "value",
    (Decimal("NaN"), Decimal("Infinity"), Decimal("-Infinity"), Decimal("0"), Decimal("-1")),
)
def test_rejects_invalid_equity_values(value: Decimal) -> None:
    with pytest.raises(ValueError):
        EquityCurveData((ts(1),), (value,), (Decimal("0"),))


@pytest.mark.parametrize(
    "value", (Decimal("NaN"), Decimal("Infinity"), Decimal("-Infinity"), Decimal("0.01"))
)
def test_rejects_invalid_drawdown_values(value: Decimal) -> None:
    with pytest.raises(ValueError):
        EquityCurveData((ts(1),), (Decimal("100"),), (value,))


def test_rejects_non_decimal_equity_values() -> None:
    with pytest.raises(ValueError, match="finite Decimal"):
        EquityCurveData((ts(1),), (Decimal("100"),), (Decimal("0"),))


def test_rejects_non_decimal_drawdown_values() -> None:
    with pytest.raises(ValueError, match="finite Decimal"):
        EquityCurveData((ts(1),), (Decimal("100"),), (Decimal("0"),))


def test_rejects_descending_timestamps() -> None:
    with pytest.raises(ValueError, match="ordered ascending"):
        EquityCurveData(
            (ts(2), ts(1)),
            (Decimal("100"), Decimal("101")),
            (Decimal("0"), Decimal("0")),
        )


def test_equal_timestamps_are_allowed() -> None:
    curve = EquityCurveData(
        (ts(1), ts(1)),
        (Decimal("100"), Decimal("101")),
        (Decimal("0"), Decimal("0")),
    )
    assert curve.timestamps == (ts(1), ts(1))


def test_first_drawdown_must_be_zero() -> None:
    with pytest.raises(ValueError, match="first drawdown"):
        EquityCurveData(
            (ts(1),),
            (Decimal("100"),),
            (Decimal("-0.01"),),
        )


def test_empty_curve_is_valid() -> None:
    curve = EquityCurveData((), (), ())
    assert len(curve) == 0
    assert tuple(curve) == ()
