"""FILE: tests/unit/test_run_strategy_backtest.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-29
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify the strategy-aware historical backtest CLI boundary.
LAYER: tests
OWNS: Assertions for scripts.run_strategy_backtest.
DOES_NOT_OWN: strategy logic, persistence semantics, execution policy, or metrics.
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
"""

import json
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import pytest

from domain.common.timeframe import Timeframe
from domain.market_data_event import MarketDataEvent
from persistence.market_data_store import MarketDataStore
from scripts.run_strategy_backtest import main


def make_event(hour: int, high: str, low: str, close: str) -> MarketDataEvent:
    timestamp = datetime(2026, 9, 29, hour, tzinfo=timezone.utc)
    return MarketDataEvent.create(
        provider="test",
        symbol="BTCUSDT",
        timeframe=Timeframe.parse("1h"),
        event_time=timestamp,
        received_at=timestamp,
        open=Decimal("10"),
        high=Decimal(high),
        low=Decimal(low),
        close=Decimal(close),
        volume=Decimal("1"),
    )


def test_main_runs_selected_donchian_strategy(tmp_path: Path, monkeypatch) -> None:
    database = tmp_path / "market.db"
    output = tmp_path / "curve.json"

    with MarketDataStore(database) as store:
        store.write(make_event(0, "10", "8", "9"))
        store.write(make_event(1, "11", "8", "10"))
        store.write(make_event(2, "13", "9", "13"))
        store.write(make_event(3, "14", "10", "14"))

    monkeypatch.setattr(
        "sys.argv",
        [
            "run_strategy_backtest.py",
            str(database),
            str(output),
            "--strategy",
            "donchian",
            "--period",
            "2",
            "--initial-capital",
            "1000",
        ],
    )

    assert main() == 0
    assert json.loads(output.read_text(encoding="utf-8")) == {
        "timestamps": [
            "2026-09-29T00:00:00+00:00",
            "2026-09-29T01:00:00+00:00",
            "2026-09-29T02:00:00+00:00",
            "2026-09-29T03:00:00+00:00",
        ],
        "equity": ["1000", "1000", "1000", "1076.923076923076923076923077"],
        "drawdown": ["0", "0", "0", "0"],
    }


def test_main_rejects_unknown_strategy(tmp_path: Path, monkeypatch) -> None:
    database = tmp_path / "market.db"
    output = tmp_path / "curve.json"

    with MarketDataStore(database):
        pass

    monkeypatch.setattr(
        "sys.argv",
        [
            "run_strategy_backtest.py",
            str(database),
            str(output),
            "--strategy",
            "unknown",
        ],
    )

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 2


def test_main_requires_at_least_two_events(tmp_path: Path, monkeypatch) -> None:
    database = tmp_path / "market.db"
    output = tmp_path / "curve.json"

    with MarketDataStore(database) as store:
        store.write(make_event(0, "10", "8", "9"))

    monkeypatch.setattr(
        "sys.argv",
        [
            "run_strategy_backtest.py",
            str(database),
            str(output),
            "--strategy",
            "donchian",
        ],
    )

    with pytest.raises(ValueError, match="at least 2 events"):
        main()
