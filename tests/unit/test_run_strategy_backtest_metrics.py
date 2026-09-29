"""FILE: tests/unit/test_run_strategy_backtest_metrics.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-29
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify metrics serialization at the strategy backtest CLI boundary.
LAYER: tests
OWNS: Assertions for metrics output from scripts.run_strategy_backtest.
DOES_NOT_OWN: metric calculation semantics, strategy logic, persistence, execution.
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
"""

import json
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from domain.common.timeframe import Timeframe
from domain.market_data_event import MarketDataEvent
from persistence.market_data_store import MarketDataStore
from scripts.run_strategy_backtest import main


def make_event(hour: int, close: str) -> MarketDataEvent:
    timestamp = datetime(2026, 9, 29, hour, tzinfo=timezone.utc)
    price = Decimal(close)
    return MarketDataEvent.create(
        provider="test",
        symbol="BTCUSDT",
        timeframe=Timeframe.parse("1h"),
        event_time=timestamp,
        received_at=timestamp,
        open=price,
        high=price,
        low=price,
        close=price,
        volume=Decimal("1"),
    )


def test_main_serializes_performance_metrics(tmp_path: Path, monkeypatch) -> None:
    database = tmp_path / "market.db"
    output = tmp_path / "curve.json"

    with MarketDataStore(database) as store:
        for hour, close in enumerate(("100", "101", "103", "102")):
            store.write(make_event(hour, close))

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
            "100",
        ],
    )

    assert main() == 0
    payload = json.loads(output.read_text(encoding="utf-8"))

    assert payload["metrics"] == {
        "observations": 4,
        "initial_equity": "100",
        "final_equity": "99.02912621359223300970873786",
        "total_return": "-0.0097087378640776699029126214",
        "max_drawdown": "-0.0097087378640776699029126214",
    }
