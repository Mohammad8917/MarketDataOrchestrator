"""Contract tests for the equity curve boundary."""

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from shared.contracts.equity_curve import EquityCurveData


def _time() -> datetime:
    return datetime(2026, 10, 2, tzinfo=timezone.utc)


def _valid() -> EquityCurveData:
    return EquityCurveData(
        timestamps=(_time(),),
        equity=(Decimal("100"),),
        drawdown=(Decimal("0"),),
    )


def test_equity_curve_accepts_valid_data() -> None:
    assert len(_valid()) == 1


@pytest.mark.parametrize("value", [[], None, "timestamps"])
def test_equity_curve_rejects_non_tuple_sequences(value: object) -> None:
    with pytest.raises(ValueError, match="timestamps must be a tuple"):
        EquityCurveData(
            timestamps=value,  # type: ignore[arg-type]
            equity=(Decimal("100"),),
            drawdown=(Decimal("0"),),
        )


@pytest.mark.parametrize("value", ["2026-10-02T00:00:00Z", None, 1])
def test_equity_curve_rejects_invalid_timestamp_runtime_types(value: object) -> None:
    with pytest.raises(ValueError, match="timestamps must contain datetime values"):
        EquityCurveData(
            timestamps=(value,),  # type: ignore[arg-type]
            equity=(Decimal("100"),),
            drawdown=(Decimal("0"),),
        )


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("equity", None, "equity must be a tuple"),
        ("drawdown", None, "drawdown must be a tuple"),
    ],
)
def test_equity_curve_rejects_invalid_value_containers(
    field: str,
    value: object,
    message: str,
) -> None:
    values: dict[str, object] = {
        "timestamps": (_time(),),
        "equity": (Decimal("100"),),
        "drawdown": (Decimal("0"),),
    }
    values[field] = value
    with pytest.raises(ValueError, match=message):
        EquityCurveData(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "value",
    [True, "2026-10-02T00:00:00Z", None],
)
def test_equity_curve_rejects_invalid_drawdown_runtime_values(value: object) -> None:
    with pytest.raises(ValueError, match="drawdown values must be finite Decimal values"):
        EquityCurveData(
            timestamps=(_time(),),
            equity=(Decimal("100"),),
            drawdown=(value,),  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "value",
    [Decimal("NaN"), Decimal("Infinity"), Decimal("-Infinity")],
)
def test_equity_curve_rejects_non_finite_equity_values(value: Decimal) -> None:
    with pytest.raises(ValueError, match="equity values must be finite Decimal values"):
        EquityCurveData(
            timestamps=(_time(),),
            equity=(value,),
            drawdown=(Decimal("0"),),
        )


def test_equity_curve_rejects_non_utc_timestamp() -> None:
    from datetime import timedelta

    with pytest.raises(ValueError, match="timestamps must be UTC"):
        EquityCurveData(
            timestamps=(datetime(2026, 10, 2, tzinfo=timezone(timedelta(hours=2))),),
            equity=(Decimal("100"),),
            drawdown=(Decimal("0"),),
        )


def test_equity_curve_rejects_unordered_timestamps() -> None:
    first = datetime(2026, 10, 2, tzinfo=timezone.utc)
    second = datetime(2026, 10, 1, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="timestamps must be ordered ascending"):
        EquityCurveData(
            timestamps=(first, second),
            equity=(Decimal("100"), Decimal("110")),
            drawdown=(Decimal("0"), Decimal("-0.1")),
        )


def test_equity_curve_rejects_nonzero_initial_drawdown() -> None:
    with pytest.raises(ValueError, match="first drawdown must be zero"):
        EquityCurveData(
            timestamps=(_time(),),
            equity=(Decimal("100"),),
            drawdown=(Decimal("-0.01"),),
        )
