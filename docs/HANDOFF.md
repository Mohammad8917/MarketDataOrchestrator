# HANDOFF

## Current verified milestone

- Canonical branch: `audit/fix-known-compliance-gaps`
- Last protected source SHA: `26714e17c4cc06a138c43653f2e5195bad4e883e`
- Protected CI run: Compliance CI #590
- GitHub Actions run: https://github.com/Mohammad8917/MarketDataOrchestrator/actions/runs/36127907249
- Compliance gates: **G01–G07 PASS (7/7)**
- Current branch head: `4308ec3a6072c462cfa8d1dccef0967e5950d5a8` (auto-generated `PROJECT_STATE.md` only; not a new protected product/source milestone)
- Product direction: Product-first; Compliance-as-guardrail.

## Runtime status

```
MarketDataEvent
      ↓
MarketDataStore
      ↓
BacktestEngine
      ↓
EquityCurve
      ↓
scripts/run_backtest.py
```

- MarketDataStore orphan: **RESOLVED**
- BacktestEngine: **IMPLEMENTED** as minimal `SimpleBacktestEngine` buy-and-hold path.
- EquityCurve: **IMPLEMENTED** as immutable `EquityCurveData` while preserving the existing `EquityCurve` Protocol.
- First production runtime consumer: **`scripts/run_backtest.py`**
- End-to-end verification: persisted fake events → replay → backtest → equity curve.

## Next product slice

**Binance Provider**

- Target: `ingestion/providers/binance_provider.py`
- Existing boundary: `ingestion/interfaces/market_provider.py`
- Public API only; no API key required.
- Provider implementation must remain behind the existing provider boundary.
- No Binance-specific dependency may leak into BacktestEngine, EquityCurve, or core domain contracts.
- Consumer-first: verify the existing provider consumer/contract before implementation.
- New SHA must restart the protected gate chain from G01.

## Evidence rule

The protected evidence is the GitHub Actions run attached to the exact source SHA above, not a claim written in this handoff.

The earlier milestone SHA `a19078c02395f6ead9ea63793d5e3f10fa53bd04` was independently verified by GitHub Actions Compliance CI #588:
https://github.com/Mohammad8917/MarketDataOrchestrator/actions/runs/36127212491

The documentation milestone `26714e17c4cc06a138c43653f2e5195bad4e883e` was then independently verified by Compliance CI #590:
https://github.com/Mohammad8917/MarketDataOrchestrator/actions/runs/36127907249

Any older handoff text claiming that G04, BacktestEngine, EquityCurve, or the production consumer is still unverified is stale relative to these protected CI runs.