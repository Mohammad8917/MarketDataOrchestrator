# ADR 0040: Backtest Setup Replay v1

- **Status:** Accepted
- **Date:** 2026-10-02
- **Scope:** Backtest setup replay
- **Contract:** `backtest_setup_replay_boundary` v1.0.0
- **Input contract:** `setup_evaluation_boundary` v1.0.0

## Decision

Define a deterministic Backtest replay consumer for point-in-time setup evaluation.

The replay:

1. Rejects empty request sequences.
2. Requires strictly increasing `event_time`.
3. Requires the supplied evaluator to implement the canonical `Setup` protocol.
4. Delegates exactly once per request, preserving request order.
5. Requires each output `event_time` to equal its request `event_time`.
6. Returns an immutable tuple of outputs.

The replay consumer does not create setup methodology, access providers, mutate persistence, or own cost, liquidity, risk, confirmation, decision, or trading semantics.

## Multi-market scope

The consumer is market-agnostic and applies equally to Crypto, Forex, and Gold. No provider, symbol, or asset-class branching is introduced.

## Rationale

`SetupOutput` currently carries `event_time` but not `source_event_id`; the replay therefore validates the provenance field that the existing v1 output contract can actually guarantee and does not invent a new field outside the contract slice.

## Revisit

Revisit only through a versioned contract change if stronger output provenance becomes an explicit requirement.
