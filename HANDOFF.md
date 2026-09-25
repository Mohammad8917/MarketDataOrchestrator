# HANDOFF

## Current State (2026-09-25)
- SHA: 820630b2251e08776f9aa1e0bab8dcd0e0987f9e
- Branch: audit/fix-known-compliance-gaps
- Gates: G01–G07 ✅ green
- Status: 7/7 gates green; Binance provider implemented and covered by integration tests
- Binance live smoke: manual-only; blocked by HTTP 451 from the GitHub-hosted runner; this is external access policy, not a G01–G07 failure

## Path
Product-First + Compliance-as-Guardrail
- 7 gates = guardrail, not goal
- Focus: product
- No new ADR, no new gate

## Interface Chain (Working)
Binance → MarketDataEvent → MarketDataStore → BacktestEngine → EquityCurve

## Implemented
- ingestion/providers/binance_provider.py ✅
- domain/market_data_event.py ✅
- persistence/market_data_store.py ✅ (SQLite)
- backtest/engine.py ✅ (SimpleBacktestEngine)
- shared/contracts/equity_curve.py ✅ (EquityCurveData)
- scripts/run_backtest.py ✅ (CLI consumer)

## Remaining
1. strategy/trend/donchian.py
2. First backtest on real BTC 4H data
3. Evaluate (Sharpe, MaxDD, WinRate)

## Locked Principles
1. README locked
2. No artificial green gates
3. Consumer before contract (ADR-0014)
4. Fail-closed
5. No lock-in (no current decision locks future paths)
6. Product-first, Compliance-as-guardrail
