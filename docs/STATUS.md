# Current Project Status

> AUTO-GENERATED. DO NOT EDIT.
> Exact SHA: 08fa40fb770856cd48a38c4f374e20e09f83db22
> Generated UTC: 2026-10-02 18:15:02 UTC
> Generated Tehran: 2026-10-02 21:45:02 +0330 (Asia/Tehran)
> Source commit UTC: 2026-10-02 18:12:05 UTC
> Source commit Tehran: 2026-10-02 21:42:05 +0330 (Asia/Tehran)
> State event: workflow_run | Run ID: 37045833564

## Canonical State

- Branch: main
- Phase: Reconciliation
- Project status: در حال توسعه

## G01–G07

| Gate | Status |
|---|---|
| G01 | SUCCESS |
| G02 | SUCCESS |
| G03 | SUCCESS |
| G04 | SUCCESS |
| G05 | SUCCESS |
| G06 | SUCCESS |
| G07 | SUCCESS |

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

- PR #138 — refactor: wire opportunity orchestrator through application container — 1762128d

## Interpretation rules

- This page is generated from the exact checked-out SHA.
- A gate is considered passed only when machine evidence for this SHA records SUCCESS.
- PENDING is not treated as success.
- Open PRs are proposals and are not part of main until merged.
- This status page never overrides GitHub Actions evidence.
