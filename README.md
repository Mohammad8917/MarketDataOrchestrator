# MarketDataOrchestrator

![Compliance CI](https://github.com/Mohammad8917/MarketDataOrchestrator/actions/workflows/ci.yml/badge.svg?branch=main)

Architecture-first market-data orchestration project for Python 3.13+.

## Current verified product slice

```
MarketDataEvent
    ↓
MarketDataStore
    ↓
SimpleBacktestEngine
    ↓
EquityCurveData
    ↓
scripts/run_backtest.py
```

Implemented and exercised:

- immutable `MarketDataEvent`
- SQLite-backed `MarketDataStore`
- typed `BacktestEngine` boundary
- minimal buy-and-hold backtest execution
- immutable `EquityCurveData`
- end-to-end persistence → replay → backtest integration

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
