"""FILE: tests/unit/test_run_strategy_comparison.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-29
DATE_PERSIAN: 1405-07-07
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify the strategy comparison CLI consumer boundary.
LAYER: tests
OWNS: Assertions for scripts.run_strategy_comparison.
DOES_NOT_OWN: strategy logic, backtest execution, persistence semantics, or ranking policy.
DEPENDENCIES: datetime, decimal, json, pathlib, domain.common.timeframe, domain.market_data_event, persistence.market_data_store, scripts.run_strategy_comparison, shared.contracts.equity_curve, pytest
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

import json
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from domain.common.timeframe import Timeframe
from domain.market_data_event import MarketDataEvent
from persistence.market_data_store import MarketDataStore
from scripts.run_strategy_comparison import main
from shared.contracts.equity_curve import EquityCurveData


def make_event(hour: int) -> MarketDataEvent:
    timestamp = datetime(2026, 9, 29, hour, tzinfo=timezone.utc)
    return MarketDataEvent.create(
        provider="test",
        symbol="BTCUSDT",
        timeframe=Timeframe.parse("1h"),
        event_time=timestamp,
        received_at=timestamp,
        open=Decimal("10"),
        high=Decimal("11"),
        low=Decimal("9"),
        close=Decimal("10"),
        volume=Decimal("1"),
    )


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


def test_main_writes_deterministic_comparison(
    tmp_path: Path,
    monkeypatch,
) -> None:
    database = tmp_path / "market.db"
    output = tmp_path / "comparison.json"

    with MarketDataStore(database) as store:
        store.write(make_event(0))
        store.write(make_event(1))

    def fake_run(
        events: tuple[MarketDataEvent, ...],
        *,
        registry,
        strategy_name: str,
        period: int,
        initial_capital: Decimal,
    ) -> EquityCurveData:
        assert len(events) == 2
        assert period == 20
        assert initial_capital == Decimal("1000")
        assert registry.names()
        return make_curve("110" if strategy_name == "zeta" else "90")

    monkeypatch.setattr(
        "scripts.run_strategy_comparison.run",
        fake_run,
    )
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_strategy_comparison.py",
            str(database),
            str(output),
            "--strategies",
            "zeta",
            "alpha",
            "--period",
            "20",
            "--initial-capital",
            "1000",
        ],
    )

    assert main() == 0
    assert json.loads(output.read_text(encoding="utf-8")) == {
        "strategies": [
            {
                "name": "alpha",
                "metrics": {
                    "observations": 2,
                    "initial_equity": "100",
                    "final_equity": "90",
                    "total_return": "-0.1",
                    "max_drawdown": "-0.1",
                },
            },
            {
                "name": "zeta",
                "metrics": {
                    "observations": 2,
                    "initial_equity": "100",
                    "final_equity": "110",
                    "total_return": "0.1",
                    "max_drawdown": "0",
                },
            },
        ],
    }


def test_main_requires_at_least_two_strategies(
    tmp_path: Path,
    monkeypatch,
) -> None:
    database = tmp_path / "market.db"
    output = tmp_path / "comparison.json"

    with MarketDataStore(database) as store:
        store.write(make_event(0))
        store.write(make_event(1))

    monkeypatch.setattr(
        "sys.argv",
        [
            "run_strategy_comparison.py",
            str(database),
            str(output),
            "--strategies",
            "donchian",
        ],
    )

    try:
        main()
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("comparison CLI must require at least two strategies")
