"""Run the complete local test suite with the same coverage threshold used by CI.

This is a local verification helper. GitHub Actions remains the authoritative
source of repository compliance evidence.
"""

from __future__ import annotations

import subprocess  # nosec B404 -- arguments are fixed local verification commands.
import sys


COVERAGE_INCLUDE = ",".join(
    (
        "domain/market_data_event.py",
        "persistence/market_data_store.py",
        "shared/contracts/equity_curve.py",
        "backtest/engine.py",
        "ingestion/providers/binance_provider.py",
    )
)


def run(*args: str) -> None:
    # nosec B603 -- command/module arguments are fixed by this local test runner.
    subprocess.run((sys.executable, "-m", *args), check=True)


def main() -> None:
    run("coverage", "erase")
    run("coverage", "run", "--branch", "-m", "pytest", "-q")
    run(
        "coverage",
        "report",
        "-m",
        f"--include={COVERAGE_INCLUDE}",
        "--fail-under=100",
    )


if __name__ == "__main__":
    main()
