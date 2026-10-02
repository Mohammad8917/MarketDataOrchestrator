# PROJECT INFO

> AUTO-GENERATED FROM THE CANONICAL CHECKED-OUT STATE.

## Identity

- Branch: main
- SHA: 37443ba3c5175f88f37bc4bb0a818e44a87fc4d3
- Last commit: fix: enforce full opportunity-chain temporal alignment (#143)
- Commit time: 2026-10-02T22:41:16+03:30
- Generated from commit time: 2026-10-02T22:41:16+03:30

## Verification

- G01: PENDING
- G02: PENDING
- G03: PENDING
- G04: PENDING
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
