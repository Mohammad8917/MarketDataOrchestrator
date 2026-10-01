# ADR 0007 — Confirmation Replay Consumer v1

- Status: Accepted
- Date: 2026-10-01
- Architecture: Frozen v1.0

## Decision

Add a backtest-owned confirmation replay consumer that invokes the frozen SignalConfirmation contract against an ordered historical request sequence.

The replay consumer:
- requires strictly increasing event times;
- invokes the supplied confirmation methodology once per request;
- requires each output timestamp to equal its request timestamp;
- returns immutable ordered results.

## Scope

The consumer is methodology-agnostic and market-agnostic. The same replay path is valid for Crypto, Forex, and Gold.

It does not generate signals, access providers, mutate persistence, model cost or liquidity, own risk, finalize decisions, or place trades.

## Consequences

Historical confirmation behavior can be replayed deterministically and audited without future request observations.

This consumer is an evaluation/replay capability only. It does not establish profitability or trading suitability.
