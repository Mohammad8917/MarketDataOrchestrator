# ADR 0042 — Deterministic Threshold Confirmation Methodology v1

- **Status:** Accepted
- **Architecture:** Frozen v1
- **Date:** 2026-10-02

## Decision

The first executable confirmation methodology is `deterministic_threshold_confirmation_v1`.

It validates finite normalized evidence in `[-1.0, 1.0]`, computes the equal-weight arithmetic mean, and marks confirmation when the absolute score is at least `0.5`.

## Invariants

1. Empty signal collections are rejected.
2. Non-finite values are rejected.
3. Values outside `[-1.0, 1.0]` are rejected.
4. Signal names and insertion order do not change the result.
5. The score remains in `[-1.0, 1.0]`.
6. Confirmation is descriptive analytical evidence, not a trading decision.
7. The methodology is market-agnostic across Crypto, Forex, and Gold.
8. It owns neither cost, liquidity, slippage nor risk.
9. The threshold is deterministic and is not a profitability or calibration claim.

## Scope

This methodology implements the existing `signal_confirmation_boundary` without changing its contract schema.
