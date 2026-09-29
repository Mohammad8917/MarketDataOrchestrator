"""FILE: scripts/run_strategy_comparison.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-29
DATE_PERSIAN: 1405-07-07
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Run multiple historical strategy backtests and serialize a deterministic comparison report.
LAYER: scripts
OWNS: CLI argument handling, strategy run orchestration, and terminal JSON serialization.
DOES_NOT_OWN: strategy logic, backtest execution, persistence semantics, provider transport, metric calculation, or ranking policy.
DEPENDENCIES: argparse, json, decimal, pathlib, backtest.event_replayer, domain.market_data_event, persistence.market_data_store, scripts.run_strategy_backtest, shared.contracts.strategy_comparison, strategy.evaluation.strategy_comparison
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

import argparse
import json
from decimal import Decimal
from pathlib import Path

from backtest.event_replayer import EventReplayer
from domain.market_data_event import MarketDataEvent
from persistence.market_data_store import MarketDataStore
from scripts.run_strategy_backtest import (
    build_strategy_registry,
    run,
)
from shared.contracts.strategy_comparison import StrategyComparison
from strategy.evaluation.strategy_comparison import build_strategy_comparison


def build_comparison(
    events: tuple[MarketDataEvent, ...],
    *,
    strategy_names: tuple[str, ...],
    period: int,
    initial_capital: Decimal,
) -> StrategyComparison:
    registry = build_strategy_registry()
    curves = {
        name: run(
            events,
            registry=registry,
            strategy_name=name,
            period=period,
            initial_capital=initial_capital,
        )
        for name in strategy_names
    }
    return build_strategy_comparison(curves)


def save_comparison(report: StrategyComparison, path: Path) -> None:
    payload = {
        "strategies": [
            {
                "name": name,
                "metrics": {
                    "observations": metrics.observations,
                    "initial_equity": str(metrics.initial_equity),
                    "final_equity": str(metrics.final_equity),
                    "total_return": str(metrics.total_return),
                    "max_drawdown": str(metrics.max_drawdown),
                },
            }
            for name, metrics in report.entries
        ],
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run multiple historical strategy backtests and compare metrics.",
    )
    registry = build_strategy_registry()
    parser.add_argument("database", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--strategies",
        nargs="+",
        choices=registry.names(),
        default=registry.names(),
    )
    parser.add_argument("--period", type=int, default=20)
    parser.add_argument("--initial-capital", type=Decimal, default=Decimal("10000"))
    args = parser.parse_args()

    strategy_names = tuple(args.strategies)
    if len(strategy_names) < 2:
        parser.error("--strategies requires at least two strategies")

    with MarketDataStore(args.database) as store:
        events = EventReplayer(store.read_all).replay()
        report = build_comparison(
            events,
            strategy_names=strategy_names,
            period=args.period,
            initial_capital=args.initial_capital,
        )

    save_comparison(report, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
