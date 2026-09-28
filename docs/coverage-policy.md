# Coverage Policy

## G05 scope

G05 enforces **100% branch coverage** for the current product vertical-slice implementation surface:

- `domain/market_data_event.py`
- `persistence/market_data_store.py`
- `shared/contracts/equity_curve.py`
- `backtest/engine.py`
- `ingestion/providers/binance_provider.py`
- `shared/contracts/market_bar.py`
- `strategy/trend/donchian.py`
- `backtest/strategy_engine.py`
- `strategy/evaluation/performance_metrics.py`

This is an explicit scoped claim. It does **not** claim 100% coverage for every Python file in the repository.

The scope is intentionally aligned with the current executable product chain:

`MarketDataEvent → MarketDataStore → BacktestEngine → EquityCurve`, with Binance ingestion at the boundary.

## Expansion plan

Coverage scope expands in dependency order, not by arbitrary percentage targets:

1. Complete and lock coverage for the current vertical-slice files.
2. Add the next executable product component only when its production behavior and tests are ready.
3. Add that component to `coverage.ini` in the same change that establishes its test contract.
4. Keep 100% branch coverage for every file already inside the scope.
5. Extend the scope toward the remaining production modules, including analysis/indicator and validation code, before treating repository-wide coverage as complete.

Unimplemented skeletons and intentionally non-product infrastructure are not silently counted as covered. They enter the scope when they become executable product responsibilities.

## CI rule

The Compliance CI G05 job uses `coverage.ini` as the single source of truth for the scoped report and requires `fail_under = 100`. Evidence artifacts may contain repository-wide execution data, but the G05 pass/fail claim is limited to the files listed in this policy.
