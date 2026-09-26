# HANDOFF

## Canonical state

- Canonical branch: `main`
- Current main SHA must be verified from GitHub before relying on this document.
- G01–G07 definitions, ordering, thresholds, and failure semantics are locked.
- Protected CI evidence is authoritative; documentation never substitutes for the exact-SHA Actions result.

## Product direction

Product-First + Compliance-as-Guardrail.

The seven verification gates are guardrails, not the product goal. No artificial green gate, no gate weakening, and no new gate.

## Current executable slice

```
Binance
    ↓
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

## Current provider status

- Executable exchange/provider implementations: 1 / 15
- Implemented provider: Binance public market-data provider
- Live Binance smoke is separate from G01–G07 and is manual-only.

## Verification rules

1. Every new SHA restarts verification from G01.
2. Claims require machine-verifiable evidence bound to the exact source SHA.
3. Fail-closed: a failed gate remains failed until the underlying cause is corrected.
4. Consumer before contract.
5. Interface-first.
6. Vertical slice before horizontal expansion.

## Known open controls

- G03 implementation/skeleton inventory remains an active program; historical counts are not current completion evidence.
- G06 transitive dependency reproducibility remains NOT VERIFIED until the committed lock, integrity, CI-install, reproducibility, and provenance controls defined by ADR-0010 are actually executed.

## Next product work

Continue the next executable product slice only after its consumer boundary, contract, implementation, tests, and exact-SHA G01–G07 evidence are established.
