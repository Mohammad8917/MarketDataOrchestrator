# PROJECT_STATE.md

> AUTO-GENERATED. DO NOT EDIT.
> Canonical branch: main
> Exact checked-out SHA: 7bd86f83810a39334c62b94402a941a70a3c166b
> This snapshot is informational; exact GitHub Actions evidence is authoritative.

## 1. Current State

- Branch: main
- SHA: 7bd86f83810a39334c62b94402a941a70a3c166b
- Last commit: chore: reconcile unapplied GitHub updates [skip ci]
- Phase: Product development / repository synchronization
- Exact-SHA gate evidence: NOT VERIFIED for this SHA

## 2. Gate Status

| Gate | Status |
|---|---|
| G01 | PENDING |
| G02 | PENDING |
| G03 | PENDING |
| G04 | PENDING |
| G05 | PENDING |
| G06 | PENDING |
| G07 | PENDING |

PENDING is fail-closed informational state: it is not a failure and is not a PASS claim.

## 3. Current Executable Product Surface

| Capability | Present |
|---|---|
| MarketDataEvent | YES |
| MarketDataStore | YES |
| SimpleBacktestEngine | YES |
| EquityCurveData | YES |
| BinanceProvider | YES |
| MarketBar | YES |
| DonchianStrategy | YES |
| StrategyBacktestEngine | YES |
| PerformanceMetrics | YES |
| Regime Analysis | YES |
| Volatility State | YES |
| Regime Analysis Replay | YES |
| Market Structure Engine | YES |

## 4. Architecture Direction

Market Data → Data Quality → Time Alignment → Market Structure → Regime/Uncertainty/Volatility → Strategy Sensors → Setup → MTF Confirmation → Liquidity/Cost/Expected Edge → Risk → Decision → Audit/Evaluation

## 5. Provider Target

The canonical provider inventory is config/exchanges.yaml.

- Target: 15
- Implemented: 1
- Planned: 14
- Implemented provider: Binance

## 6. Markets

- Crypto: executable Binance path present.
- Forex: architecture target; provider implementation planned.
- Gold: architecture target; provider implementation planned.

## 7. Open Findings

- GAP-014 — Bollinger mocked-band expected-value provenance
- GAP-022 — Main/audit architecture validator fix divergence
- GAP-008 — MarketDataStore orphan
- GAP-024 — Strategy/backtest architecture policy contradiction
- GAP-025 — Layer-graph cycle detection
- GAP-026 — Cross-layer cycle regression tests
- GAP-029 — G05 coverage scope
- GAP-030 — Dependency integrity hashes
- GAP-031 — Repository-wide strict mypy enforcement
- GAP-032 — Frozen no-cycle architecture policy

Historical entries are retained in docs/GAP_REGISTER.md; their current status must be read there.

## 8. Interface Chain

MarketDataEvent
→ MarketDataStore
→ BacktestEngine
→ Strategy
→ Evaluation

Market structure is an analysis dependency and does not own strategy decisions, risk, execution, or provider I/O.

## 9. Locked Principles

1. main is canonical.
2. Exact-SHA evidence only.
3. No artificial green gates.
4. Consumer before contract implementation.
5. Interface-first.
6. Vertical slice before horizontal expansion.
7. Product-first; compliance is a guardrail.
