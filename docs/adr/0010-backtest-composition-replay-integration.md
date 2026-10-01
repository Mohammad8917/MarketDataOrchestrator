# ADR 0010 — Backtest Composition Replay Integration

- **Status:** Accepted
- **Date:** 2026-10-01
- **Scope:** Backtest replay integration
- **Markets:** Crypto, Forex, Gold

## Decision

The canonical `backtest.replay_engine.BacktestReplayEngine` owns dependency wiring for analytical replay consumers. Version 1 integrates `backtest.composition_replay.CompositionReplay` through a narrow `replay_composition()` method.

The integration delegates execution to the existing Composition Replay consumer and does not duplicate its validation or methodology.

## Boundaries

- Composition methodology remains owned by `composition`.
- Point-in-time replay semantics remain owned by `CompositionReplay`.
- The replay engine performs dependency wiring only.
- No provider I/O, persistence mutation, cost/liquidity analysis, risk evaluation, decision finalization, or trading action is introduced.
- The integration is market-agnostic and carries no Crypto, Forex, or Gold-specific assumptions.

## Rationale

This establishes one canonical Backtest entry point for the already-approved composition replay capability without creating a parallel replay implementation or prematurely coupling analysis to Decision/Risk.

## Verification

`tests/unit/test_replay_engine.py` verifies delegation equivalence, protocol-boundary type rejection, and exposure of the canonical composition replay contract.
