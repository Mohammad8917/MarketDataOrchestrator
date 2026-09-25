# MarketDataOrchestrator

![Compliance CI](https://github.com/Mohammad8917/MarketDataOrchestrator/actions/workflows/ci.yml/badge.svg?branch=main)

Architecture-first market-data orchestration project for Python 3.13+.

## Current executable product slice

```
Binance
    ↓
MarketDataEvent
    ↓
MarketDataStore
    ↓
StrategyBacktestEngine
    ↓
DonchianStrategy
    ↓
EquityCurveData
    ↓
PerformanceMetrics
```

Implemented and exercised:

- immutable `MarketDataEvent`
- SQLite-backed `MarketDataStore`
- typed `BacktestEngine` boundary
- strategy-facing shared `MarketBar` contract
- executable Donchian long/flat breakout strategy
- explicit next-bar execution semantics with no look-ahead
- immutable `EquityCurveData`
- deterministic total-return, max-drawdown, Sharpe, and positive-return-rate metrics
- focused unit and backtest coverage

## Provider status

The project targets 15 exchange/provider capabilities, but a target is not an implementation claim.

**Current executable exchange implementations: 1 / 15 (Binance).**

Binance is the next provider slice. It will be added only after its existing boundary and executable consumer are verified.

## Verification

Every material change is subject to the repository's ordered verification gates. Missing evidence is treated as **NOT VERIFIED**.

- G01 format/lint
- G02 type checking
- G03 unit/contract verification
- G04 architecture/dependency verification
- G05 coverage
- G06 security/supply-chain verification
- G07 integration/resilience verification
- G08 release verification when a release is produced

The authoritative Compliance Kit is [`docs/README.md`](docs/README.md).

## Documentation

- [Compliance Kit](docs/README.md)
- [Handoff](docs/HANDOFF.md)
- [Gap Register](docs/GAP_REGISTER.md)
- [Runbooks](docs/runbooks.md)
- [Architecture ADRs](docs/adr/)

## License

Proprietary — All Rights Reserved. See [`LICENSE`](LICENSE).
