# Architecture Overview

## Canonical direction

Market Data
→ Data Quality
→ Time Alignment
→ Market Structure
→ Regime / Uncertainty / Volatility
→ Strategy Sensors
→ Setup
→ MTF Confirmation
→ Liquidity / Cost / Expected Edge
→ Risk
→ Decision
→ Audit / Evaluation

## Executable foundation

MarketDataEvent
→ MarketDataStore
→ BacktestEngine
→ Strategy
→ Evaluation

## Market-agnostic rule

Crypto, Forex, and Gold are market contexts. Core contracts must not become provider-specific or crypto-only.

## Dependency rule

Development proceeds in dependency order. Upper layers do not own lower-layer concerns.

## Strategy boundary

Strategy sensors describe conditions. Risk, cost, decision, execution, and provider transport remain separate responsibilities.
