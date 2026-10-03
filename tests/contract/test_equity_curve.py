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


def test_equity_curve_rejects_duplicate_timestamps() -> None:
    timestamp = _time()
    with pytest.raises(ValueError, match="timestamps must be strictly increasing"):
        EquityCurveData(
            timestamps=(timestamp, timestamp),
            equity=(Decimal("100"), Decimal("101")),
            drawdown=(Decimal("0"), Decimal("-1")),
        )


def test_equity_curve_rejects_temporal_regression() -> None:
    first = _time()
    second = datetime(2026, 10, 1, 23, 59, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="timestamps must be ordered ascending"):
        EquityCurveData(
            timestamps=(first, second),
            equity=(Decimal("100"), Decimal("101")),
            drawdown=(Decimal("0"), Decimal("-1")),
        )
