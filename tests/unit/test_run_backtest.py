"""FILE: tests/unit/test_run_backtest.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-25
DATE_PERSIAN: 1405-07-03
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify the backtest CLI serialization and execution boundary.
LAYER: tests
OWNS: Assertions for scripts.run_backtest entry points.
DOES_NOT_OWN: persistence behavior, backtest policy, provider transport
DEPENDENCIES: datetime, decimal, json, pathlib, persistence.market_data_store, scripts.run_backtest
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timezone
from decimal import Decimal
import json
from pathlib import Path

from domain.common.timeframe import Timeframe
from domain.market_data_event import MarketDataEvent
from persistence.market_data_store import MarketDataStore
from scripts.run_backtest import main, save_curve
from shared.contracts.equity_curve import EquityCurveData


def make_event(hour: int, close: str) -> MarketDataEvent:
    return MarketDataEvent.create(
        provider="demo",
        symbol="BTCUSD",
        timeframe=Timeframe.parse("1h"),
        event_time=datetime(2026, 9, 24, hour, tzinfo=timezone.utc),
        received_at=datetime(2026, 9, 24, hour, 1, tzinfo=timezone.utc),
        open=Decimal(close),
        high=Decimal(close),
        low=Decimal(close),
        close=Decimal(close),
        volume=Decimal("1"),
    )


def test_save_curve_serializes_contract(tmp_path: Path) -> None:
    timestamp = datetime(2026, 9, 24, 12, tzinfo=timezone.utc)
    curve = EquityCurveData(
        timestamps=(timestamp,),
        equity=(Decimal("100"),),
        drawdown=(Decimal("0"),),
    )
    output = tmp_path / "curve.json"

    save_curve(curve, output)

    assert json.loads(output.read_text(encoding="utf-8")) == {
        "timestamps": ["2026-09-24T12:00:00+00:00"],
        "equity": ["100"],
        "drawdown": ["0"],
    }


def test_main_runs_persisted_vertical_slice(tmp_path: Path, monkeypatch) -> None:
    database = tmp_path / "market.db"
    output = tmp_path / "curve.json"

    with MarketDataStore(database) as store:
        store.write(make_event(12, "100"))
        store.write(make_event(13, "110"))

    monkeypatch.setattr(
        "sys.argv",
        ["run_backtest.py", str(database), str(output)],
    )

    assert main() == 0
    assert json.loads(output.read_text(encoding="utf-8")) == {
        "timestamps": [
            "2026-09-24T12:00:00+00:00",
            "2026-09-24T13:00:00+00:00",
        ],
        "equity": ["100", "110"],
        "drawdown": ["0", "0"],
    }
