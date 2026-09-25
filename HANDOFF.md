# HANDOFF

## Current State (2026-09-25)
- SHA: a19078c02395f6ead9ea63793d5e3f10fa53bd04
- Branch: audit/fix-known-compliance-gaps
- Gates: G01–G07 ✅ green, G08 ⏭
- Status: 7/7 green, first executable vertical slice

## Path
Product-First + Compliance-as-Guardrail
- 7 gates = guardrail, not goal
- Focus: product
- No new ADR, no new gate

## Interface Chain (Working)
Binance (planned) → MarketDataEvent → MarketDataStore → BacktestEngine → EquityCurve

## Implemented
- domain/market_data_event.py ✅
- persistence/market_data_store.py ✅ (SQLite)
- backtest/engine.py ✅ (SimpleBacktestEngine)
- shared/contracts/equity_curve.py ✅ (EquityCurveData)
- scripts/run_backtest.py ✅ (CLI consumer)

## Remaining
1. ingestion/providers/binance_provider.py
2. strategy/trend/donchian.py
3. First backtest on real BTC 4H data
4. Evaluate (Sharpe, MaxDD, WinRate)

## Locked Principles
1. README locked
2. No artificial green gates
3. Consumer before contract (ADR-0014)
4. Fail-closed
5. No lock-in (no current decision locks future paths)
6. Product-first, Compliance-as-guardrail
