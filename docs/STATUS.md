# Current Project Status

> AUTO-GENERATED. DO NOT EDIT.
> Exact SHA: f80ce6f27c3f8f52b956bcf7bbdaf289b53590c2
> Generated UTC: 2026-10-01 18:46:41 UTC
> Generated Tehran: 2026-10-01 22:16:41 +0330 (Asia/Tehran)
> Source commit UTC: 2026-10-01 18:45:17 UTC
> Source commit Tehran: 2026-10-01 22:15:17 +0330 (Asia/Tehran)
> State event: workflow_run | Run ID: 36909189841

## Canonical State

- Branch: main
- Phase: Reconciliation
- Project status: در حال توسعه

## G01–G07

| Gate | Status |
|---|---|
| G01 | SUCCESS |
| G02 | SUCCESS |
| G03 | FAILURE |
| G04 | SUCCESS |
| G05 | SKIPPED |
| G06 | SKIPPED |
| G07 | SKIPPED |

## Findings

- Open: **8**
- Resolved: **19**
- Other/unclassified: **0**

## Active product surface


| Capability | File | Present on this SHA |
|---|---|---|
| MarketDataEvent | domain/market_data_event.py | YES |
| MarketDataStore | persistence/market_data_store.py | YES |
| SimpleBacktestEngine | backtest/engine.py | YES |
| EquityCurveData | shared/contracts/equity_curve.py | YES |
| BinanceProvider | ingestion/providers/binance_provider.py | YES |
| MarketBar | shared/contracts/market_bar.py | YES |
| DonchianStrategy | strategy/trend/donchian.py | YES |
| StrategyBacktestEngine | backtest/strategy_engine.py | YES |
| PerformanceMetrics | strategy/evaluation/performance_metrics.py | YES |

## Open pull requests targeting main

- No open PRs targeting main

## Interpretation rules

- This page is generated from the exact checked-out SHA.
- A gate is considered passed only when machine evidence for this SHA records SUCCESS.
- PENDING is not treated as success.
- Open PRs are proposals and are not part of main until merged.
- This status page never overrides GitHub Actions evidence.
