# HANDOFF

## Canonical state

- Canonical branch: `audit/fix-known-compliance-gaps`
- This file is the canonical handoff for the audit branch.
- `PROJECT_STATE.md` is auto-generated and is not authoritative for the audit branch because its workflow intentionally does not push state commits back onto this branch.
- The current candidate SHA is **not declared green here** unless the exact SHA has protected G01–G07 evidence.
- Last independently protected product milestone: `a19078c02395f6ead9ea63793d5e3f10fa53bd04`
- Compliance CI #588: https://github.com/Mohammad8917/MarketDataOrchestrator/actions/runs/36127212491
- Documentation verification milestone: `26714e17c4cc06a138c43653f2e5195bad4e883e`
- Compliance CI #590: https://github.com/Mohammad8917/MarketDataOrchestrator/actions/runs/36127907249
- Those protected runs are historical evidence for their exact source SHAs; they do not certify a newer SHA.

## Product direction

**Product-first + Compliance-as-Guardrail**

- G01–G07 are immutable guardrails.
- No gate definition, threshold, ordering, or failure semantics are changed to obtain a green result.
- Every new SHA restarts protected verification from G01.
- No artificial implementation or artificial evidence.

## Current executable product slice

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

## Current provider slice

- `ingestion/providers/binance_provider.py` is implemented behind the canonical provider boundary.
- Binance-specific transport details remain inside the provider boundary.
- The live Binance smoke is separate from G01–G07 and may be blocked by external runner/network policy.

## Resolved lineage/documentation findings

- Root-level duplicate `HANDOFF.md` is not canonical; `docs/HANDOFF.md` is the sole handoff location.
- README provider-count wording is explicit: 1 executable provider out of a 15-provider target.
- Root `LICENSE` exists.
- README contains the Compliance CI badge.
- PR #1 is merged; its final self-review and protected evidence remain historical audit records.

## Open findings that remain real

1. **G06 transitive dependency reproducibility** — not yet verified. A green G06 claim requires a committed resolved dependency/integrity artifact and same-SHA CI verification.
2. **G03 executable skeleton inventory** — active implementation program remains fail-closed.
3. **G03 architecture scope / consumer viability** — future-consumer-only modules must be bound to a justified executable phase or formally reclassified; speculative consumers must not be added.
4. **GAP-022 main/audit architecture-validator divergence** — audit reconciliation remains canonical; do not transplant the older main fix over it.

## Next product slice

**Donchian strategy vertical slice**

Bottom-up order:

1. Verify the existing strategy-facing market-bar boundary.
2. Implement the Donchian strategy at the strategy layer.
3. Bind it to an executable strategy-aware backtest consumer.
4. Add known-value/no-lookahead tests.
5. Add deterministic performance metrics only after the equity-curve consumer boundary is verified.
6. Run the full protected G01–G07 chain for the resulting SHA.
7. Only after protected verification, proceed to real BTC 4H evaluation.

## Evidence rule

Protected CI evidence is authoritative. A handoff statement never substitutes for the GitHub Actions result attached to the exact source SHA.
