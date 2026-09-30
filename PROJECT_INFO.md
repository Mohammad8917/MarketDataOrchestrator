# PROJECT INFO

> AUTO-GENERATED FROM THE CANONICAL CHECKED-OUT STATE.

## Identity

- Branch: main
- SHA: 89770d32f698fbcd1320c885b8ab296e4e598615
- Last commit: chore: synchronize repository truth [skip ci]
- Commit time: 2026-09-30T22:35:12Z
- Generated from commit time: 2026-09-30T22:35:12Z

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
