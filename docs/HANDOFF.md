# HANDOFF

## Candidate product milestone

- Candidate branch: `product/donchian-vertical-slice`
- Candidate SHA: `04780d9c85d6f0f2d1e3d9efa697f2c238db1a9b` before this documentation-only update
- Protected CI evidence is authoritative; documentation never substitutes for a successful run on the exact final SHA.
- Product direction: Product-First + Compliance-as-Guardrail.
- G01–G07 remain mandatory guardrails, not the product goal.

## Executable product slice

```
Binance
    ↓
MarketDataEvent
    ↓
MarketDataStore
    ↓
MarketBar
    ↓
DonchianStrategy
    ↓
StrategyBacktestEngine
    ↓
EquityCurveData
    ↓
PerformanceMetrics
```

Implemented:

- Binance public market provider
- immutable canonical MarketDataEvent
- SQLite MarketDataStore
- shared strategy-facing MarketBar contract
- executable Donchian long/flat breakout strategy
- explicit next-bar execution semantics
- no-lookahead strategy tests
- immutable EquityCurveData
- deterministic total return, max drawdown, annualized Sharpe, and positive-return-rate metrics
- focused unit and backtest coverage

## Remaining product evidence

1. Capture a real BTCUSDT 4H historical dataset through the provider path.
2. Persist that dataset through MarketDataStore.
3. Run the Donchian strategy through StrategyBacktestEngine.
4. Publish reproducible backtest evidence, including Sharpe, MaxDD, and trade-level win rate.
5. Keep live-provider access failures attributable to external network policy separate from product-code verification.

## Verification rule

The exact final product SHA must have successful protected CI before it is treated as verified. A green run on an earlier SHA is not evidence for a later SHA.

## Locked principles

1. Product-first; compliance is a guardrail.
2. No artificial green gates.
3. Consumer before contract.
4. Fail closed.
5. No lock-in of future strategy or provider choices.
6. One coherent product slice, then verification, then merge.
