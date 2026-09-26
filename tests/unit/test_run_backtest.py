"""FILE: tests/unit/test_run_backtest.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-09-25
DATE_PERSIAN: 1405-07-03
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify the backtest CLI serialization, validation, and execution boundary.
LAYER: tests
OWNS: Assertions for scripts.run_backtest entry points.
DOES_NOT_OWN: persistence behavior, backtest policy, provider transport
DEPENDENCIES: datetime, decimal, json, pathlib, pytest, persistence.market_data_store, scripts.run_backtest
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

import json
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import pytest

from domain.common.timeframe import Timeframe
from domain.market_data_event import MarketDataEvent
from persistence.market_data_store import MarketDataStore
from scripts.run_backtest import main, save_curve
from shared.contracts.equity_curve import EquityCurveData


def make_event(hour: int, close: str) -> MarketDataEvent:
    value = Decimal(close)
    return MarketDataEvent.create(
        provider="demo",
        symbol="BTCUSD",
        timeframe=Timeframe.parse("1h"),
        event_time=datetime(2026, 9, 24, hour, tzinfo=timezone.utc),
        received_at=datetime(2026, 9, 24, hour, 1, tzinfo=timezone.utc),
        open=value,
        high=value,
        low=value,
        close=value,
        volume=Decimal("1"),
    )


def read_output(path: Path) -> dict[str, list[str]]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_save_curve_preserves_exact_contract_values(tmp_path: Path) -> None:
    curve = EquityCurveData(
        timestamps=(
            datetime(2026, 9, 24, 12, tzinfo=timezone.utc),
            datetime(2026, 9, 24, 13, tzinfo=timezone.utc),
        ),
        equity=(Decimal("100.125"), Decimal("99.875")),
        drawdown=(Decimal("0"), Decimal("-0.0025")),
    )
    output = tmp_path / "curve.json"

    save_curve(curve, output)

    assert read_output(output) == {
        "timestamps": [
            "2026-09-24T12:00:00+00:00",
            "2026-09-24T13:00:00+00:00",
        ],
        "equity": ["100.125", "99.875"],
        "drawdown": ["0", "-0.0025"],
    }
    assert "100.125" in output.read_text(encoding="utf-8")
    assert "99.875" in output.read_text(encoding="utf-8")


def test_save_curve_overwrites_existing_output_deterministically(tmp_path: Path) -> None:
    curve = EquityCurveData(
        timestamps=(datetime(2026, 9, 24, 12, tzinfo=timezone.utc),),
        equity=(Decimal("100"),),
        drawdown=(Decimal("0"),),
    )
    output = tmp_path / "curve.json"
    output.write_text("stale output", encoding="utf-8")

    save_curve(curve, output)
    first = output.read_text(encoding="utf-8")
    save_curve(curve, output)
    second = output.read_text(encoding="utf-8")

    assert first == second
    assert first.endswith("\n") is False


def test_save_curve_rejects_missing_parent_instead_of_silent_loss(
    tmp_path: Path,
) -> None:
    curve = EquityCurveData(
        timestamps=(datetime(2026, 9, 24, 12, tzinfo=timezone.utc),),
        equity=(Decimal("100"),),
        drawdown=(Decimal("0"),),
    )
    output = tmp_path / "missing" / "curve.json"

    with pytest.raises(FileNotFoundError):
        save_curve(curve, output)


def test_main_runs_full_vertical_slice_and_preserves_drawdown(tmp_path: Path, monkeypatch) -> None:
    database = tmp_path / "market.db"
    output = tmp_path / "curve.json"

    with MarketDataStore(database) as store:
        store.write(make_event(12, "100"))
        store.write(make_event(13, "110"))
        store.write(make_event(14, "90"))

    monkeypatch.setattr(
        "sys.argv",
        ["run_backtest.py", str(database), str(output)],
    )

    assert main() == 0
    assert read_output(output) == {
        "timestamps": [
            "2026-09-24T12:00:00+00:00",
            "2026-09-24T13:00:00+00:00",
            "2026-09-24T14:00:00+00:00",
        ],
        "equity": ["100", "110", "90"],
        "drawdown": ["0", "0", "-0.1818181818181818181818181818"],
    }


def test_main_handles_empty_history_as_valid_empty_curve(tmp_path: Path, monkeypatch) -> None:
    database = tmp_path / "empty.db"
    output = tmp_path / "curve.json"

    with MarketDataStore(database):
        pass

    monkeypatch.setattr(
        "sys.argv",
        ["run_backtest.py", str(database), str(output)],
    )

    assert main() == 0
    assert read_output(output) == {
        "timestamps": [],
        "equity": [],
        "drawdown": [],
    }


def test_main_requires_both_positional_arguments(monkeypatch) -> None:
    monkeypatch.setattr("sys.argv", ["run_backtest.py"])

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 2
