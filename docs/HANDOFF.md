# HANDOFF

## Canonical state

- Canonical branch: `main`
- Current main SHA must be verified from GitHub before relying on this document.
- G01–G07 definitions, ordering, thresholds, and failure semantics are locked.
- Protected CI evidence is authoritative; documentation never substitutes for the exact-SHA Actions result.
- `PROJECT_STATE.md` is an automatically generated diagnostic snapshot; it may lag while state automation is processing a new SHA.

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

## Product progression rule

New product work must follow the dependency order:

1. executable consumer boundary;
2. interface/contract;
3. smallest valid implementation;
4. strict unit and integration tests;
5. exact-SHA G01–G07 verification;
6. merge into `main`;
7. only then treat the capability as current functionality.

The currently active unmerged work must be verified from GitHub pull requests; it must not be copied into this canonical handoff as if it were already released.

## Audit reconciliation history

- The audit lineage `audit/fix-known-compliance-gaps` was reconciled against `main` from merge-base `6704cf1e02a0d7bf5a148928bd6bf47348af9698`.
- Pre-reconciliation audit candidate SHA: `49645a1975345360108860b70e5d1aee7e879c8e`.
- Its protected Compliance CI evidence was G01–G07 green on that exact SHA (Compliance CI #925, Run ID `36275094639`). This remains historical evidence and does not certify the new merge SHA.
- The root-level duplicate `HANDOFF.md` is not canonical; `docs/HANDOFF.md` is the sole handoff location.
- README provider-count wording is explicit: 1 executable provider out of a 15-provider target.
- Root `LICENSE` exists and README contains the Compliance CI badge.
- PR #1 is merged; its final self-review and protected evidence remain historical audit records.

## Current-state authority

For the exact current state, use this order:

1. `main` exact SHA on GitHub;
2. G01–G07 Actions evidence for that SHA;
3. `PROJECT_STATE.md` generated snapshot;
4. this handoff and the Gap Register for context.

`PROJECT_STATE.md` and this handoff never override exact-SHA evidence.

## Current provider slice

- `ingestion/providers/binance_provider.py` is implemented behind the canonical provider boundary.
- Binance-specific transport details remain inside the provider boundary.
- The live Binance smoke is separate from G01–G07 and may be blocked by external runner/network policy.

## Open findings that remain real

1. **G06 transitive dependency reproducibility** — not yet verified. A green G06 claim requires a committed resolved dependency/integrity artifact and same-SHA CI verification.
2. **G03 executable skeleton inventory** — active implementation program remains fail-closed.
3. **G03 architecture scope / consumer viability** — future-consumer-only modules must be bound to a justified executable phase or formally reclassified; speculative consumers must not be added.
4. **G05 scoped coverage** — 100% applies only to the files currently enumerated by the coverage policy.

## Next product slice

**Regime-to-edge integration**

Bottom-up order:

1. Preserve canonical SetupOutput and ConfirmationOutput as the upstream edge prerequisites.
2. Bind canonical RegimeAnalysisOutput into the existing edge-evaluation path using only an explicit normalized descriptive alignment value.
3. Enforce point-in-time/source-event alignment without recalculating regime analysis.
4. Add deterministic integration tests for aligned and mismatched regime observations.
5. Keep cost, liquidity, risk, decision, and execution as explicit downstream boundaries.
6. Run the full protected G01–G07 chain for the resulting SHA.
7. Keep the resulting edge score descriptive; it is not a probability, expected return, or profitability guarantee.
