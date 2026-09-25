# HANDOFF

## Canonical state

- Canonical branch: `audit/fix-known-compliance-gaps`
- Current branch state is a **candidate** until the exact candidate SHA has protected CI evidence.
- Last independently protected product milestone: `a19078c02395f6ead9ea63793d5e3f10fa53bd04`
- Compliance CI #588: https://github.com/Mohammad8917/MarketDataOrchestrator/actions/runs/36127212491
- Documentation verification milestone: `26714e17c4cc06a138c43653f2e5195bad4e883e`
- Compliance CI #590: https://github.com/Mohammad8917/MarketDataOrchestrator/actions/runs/36127907249
- Both protected runs recorded G01–G07 success for their exact source SHA.

## Runtime slice

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

- MarketDataStore runtime orphan: **RESOLVED**
- BacktestEngine: **IMPLEMENTED** as minimal buy-and-hold execution.
- EquityCurve: **IMPLEMENTED** as immutable `EquityCurveData` behind the existing `EquityCurve` Protocol.
- First production runtime consumer: `scripts/run_backtest.py`
- End-to-end integration path: persisted fake events → replay → backtest → equity curve.

## Evidence rule

Protected CI evidence is authoritative. A handoff statement never substitutes for the GitHub Actions result attached to the exact source SHA.

## Next product slice

**Binance Provider**

- Verify the existing provider boundary and executable consumer before implementation.
- Keep Binance-specific transport details inside the provider boundary.
- No provider dependency may leak into BacktestEngine, EquityCurve, or core domain contracts.
- Every new SHA restarts the protected verification chain from G01.
