# Architecture Overview

## Canonical direction

Market Data → Data Quality → Time Alignment → Market Structure → Regime/Uncertainty/Volatility → Strategy Sensors → Setup → MTF Confirmation → Liquidity/Cost/Expected Edge → Risk → Decision → Audit/Evaluation

## Executable foundation

MarketDataEvent → MarketDataStore → BacktestEngine → Strategy → Evaluation

## Market rule

Core contracts remain market-agnostic. Crypto, Forex, and Gold are represented as market contexts rather than separate architecture trees.

## Product-first rule

A capability becomes canonical only after contract, methodology, implementation, focused tests, and exact-SHA verification are present.
