# ADR 0008 — Composition Replay Consumer v1

- Status: Accepted
- Date: 2026-10-01
- Architecture: Frozen v1.0

## Decision

Add a backtest-owned composition replay consumer that invokes the frozen SignalComposer contract against an ordered historical request sequence.

The replay consumer:
- requires strictly increasing event times;
- invokes the supplied composition methodology once per request;
- requires each output timestamp to equal its request timestamp;
- returns immutable ordered results.

## Scope

The consumer is methodology-agnostic and market-agnostic. The same replay path is valid for Crypto, Forex, and Gold.

It does not generate market data, access providers, mutate persistence, perform confirmation, model cost or liquidity, own risk, finalize decisions, or place trades.

## Consequences

Historical composition behavior can be replayed deterministically and audited without future request observations.

This consumer is an evaluation/replay capability only. It does not establish profitability or trading suitability.
