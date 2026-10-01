# PROJECT INFO

> AUTO-GENERATED FROM THE CANONICAL CHECKED-OUT STATE.

## Identity

- Branch: main
- SHA: 299e3926e46a5dcf2dc51f4147c1209722b5de89
- Last commit: fix: correct repository truth workflow event expressions
- Commit time: 2026-10-01T03:28:04+03:30
- Generated from commit time: 2026-10-01T03:28:04+03:30

## Verification

- G01: SUCCESS
- G02: SUCCESS
- G03: SUCCESS
- G04: SUCCESS
- G05: SUCCESS
- G06: SUCCESS
- G07: SUCCESS

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
