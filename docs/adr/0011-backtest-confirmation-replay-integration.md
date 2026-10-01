# ADR 0011 — Backtest Confirmation Replay Integration

- **Status:** Accepted
- **Date:** 2026-10-01
- **Scope:** Backtest replay integration
- **Markets:** Crypto, Forex, Gold

## Decision

`backtest.replay_engine.BacktestReplayEngine` also wires the existing `backtest.confirmation_replay.ConfirmationReplay` consumer through `replay_confirmation()`.

The integration delegates all ordering and output validation to the existing replay consumer. It introduces no new confirmation methodology.

## Boundaries

- Confirmation methodology remains owned by `composition`.
- Point-in-time replay semantics remain owned by `ConfirmationReplay`.
- The replay engine remains dependency wiring only.
- No provider I/O, persistence mutation, cost/liquidity analysis, risk evaluation, or decision finalization is introduced.
- The integration remains market-agnostic for Crypto, Forex, and Gold.

## Verification

`tests/unit/test_replay_engine.py` verifies delegation equivalence, invalid confirmer rejection, and exposure of the canonical confirmation replay contract.
