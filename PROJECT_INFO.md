# PROJECT INFO

> AUTO-GENERATED FROM THE CANONICAL CHECKED-OUT STATE.

## Identity

- Branch: main
- SHA: 8acb7620dcfa8eb882fcb5f3ea79a312ddcde831
- Last commit: refactor: wire orchestrator through application container (#138)
- Commit time: 2026-10-02T21:47:58+03:30
- Generated from commit time: 2026-10-02T21:47:58+03:30

## Verification

- G01: SUCCESS
- G02: PENDING
- G03: SUCCESS
- G04: SUCCESS
- G05: PENDING
- G06: PENDING
- G07: PENDING

## Product surface

- MarketDataEvent: domain/market_data_event.py
- MarketDataStore: persistence/market_data_store.py
- SimpleBacktestEngine: backtest/engine.py
- EquityCurveData: shared/contracts/equity_curve.py
- BinanceProvider: ingestion/providers/binance_provider.py
- MarketBar: shared/contracts/market_bar.py
- DonchianStrategy: strategy/trend/donchian.py
- StrategyBacktestEngine: backtest/strategy_engine.py
- PerformanceMetrics: strategy/evaluation/performance_metrics.py

## Architecture direction

The repository is developed bottom-up and market-agnostic. Crypto, Forex, and Gold are product targets; provider-specific behavior remains behind ingestion boundaries.

## Canonical rules

- main is the canonical branch.
- Exact-SHA GitHub Actions evidence is authoritative for gate claims.
- Compliance is a guardrail, not the product objective.
- Strategy code does not own risk, cost, decision, or provider I/O.

## Important entry points

- README
- PROJECT_STATE.md
- docs/STATUS.md
- CHANGELOG.md
- ROADMAP.md
- docs/GAP_REGISTER.md
- docs/architecture/overview.md
- CONTRIBUTING.md
