"""FILE: scripts/run_backtest.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-25
DATE_PERSIAN: 1405-07-03
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Run the minimal historical backtest vertical slice from persisted market data.
LAYER: scripts
OWNS: CLI argument handling and terminal JSON serialization for backtest results.
DOES_NOT_OWN: backtest execution, persistence semantics, strategy logic, provider transport
DEPENDENCIES: argparse, json, pathlib, backtest.engine, persistence.market_data_store, shared.contracts.equity_curve
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from backtest.engine import SimpleBacktestEngine
from persistence.market_data_store import MarketDataStore
from shared.contracts.equity_curve import EquityCurve


def save_curve(curve: EquityCurve, path: Path) -> None:
    payload = {
        "timestamps": [timestamp.isoformat() for timestamp in curve.timestamps],
        "equity": [str(value) for value in curve.equity],
        "drawdown": [str(value) for value in curve.drawdown],
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the minimal historical backtest.")
    parser.add_argument("database", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    with MarketDataStore(args.database) as store:
        curve = SimpleBacktestEngine().run(store.read_all())
    save_curve(curve, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
