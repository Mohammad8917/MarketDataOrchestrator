"""FILE: scripts/run_strategy_backtest.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-29
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Run a selected historical strategy backtest from persisted market data.
LAYER: scripts
OWNS: CLI argument handling, strategy selection, and terminal JSON serialization.
DOES_NOT_OWN: persistence semantics, strategy logic, backtest execution, provider transport, or metrics.
DEPENDENCIES: argparse, json, pathlib, decimal, backtest.event_replayer, backtest.strategy_engine, domain.market_data_event, persistence.market_data_store, strategy.trend.donchian
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
"""

from __future__ import annotations

import argparse
import json
from decimal import Decimal
from pathlib import Path

from backtest.event_replayer import EventReplayer
from backtest.strategy_engine import StrategyBacktestEngine
from domain.market_data_event import MarketDataEvent
from persistence.market_data_store import MarketDataStore
from shared.contracts.equity_curve import EquityCurve
from strategy.trend.donchian import DonchianStrategy


def save_curve(curve: EquityCurve, path: Path) -> None:
    payload = {
        "timestamps": [timestamp.isoformat() for timestamp in curve.timestamps],
        "equity": [str(value) for value in curve.equity],
        "drawdown": [str(value) for value in curve.drawdown],
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def build_strategy(name: str, period: int) -> DonchianStrategy:
    if name == "donchian":
        return DonchianStrategy(period=period)
    raise ValueError(f"unknown strategy: {name}")


def run(
    events: tuple[MarketDataEvent, ...],
    *,
    strategy_name: str,
    period: int,
    initial_capital: Decimal,
) -> EquityCurve:
    strategy = build_strategy(strategy_name, period)
    return StrategyBacktestEngine(initial_capital).run(events, strategy)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run a selected historical strategy backtest.",
    )
    parser.add_argument("database", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--strategy", choices=("donchian",), required=True)
    parser.add_argument("--period", type=int, default=20)
    parser.add_argument("--initial-capital", type=Decimal, default=Decimal("10000"))
    args = parser.parse_args()

    with MarketDataStore(args.database) as store:
        events = EventReplayer(store.read_all).replay()
        curve = run(
            events,
            strategy_name=args.strategy,
            period=args.period,
            initial_capital=args.initial_capital,
        )

    save_curve(curve, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
