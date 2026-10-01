# ADR 0004 — Deterministic Composition Methodology v1

- Status: Accepted
- Architecture: Frozen v1
- Date: 2026-10-01

## Decision

The first executable composition methodology is deterministic_equal_weight_mean_v1.

It accepts upstream analytical evidence represented as finite normalized values in the closed interval [-1.0, 1.0]. Every supplied signal has equal weight. The output is the arithmetic mean.

## Invariants

1. Empty signal collections are rejected.
2. Non-finite values are rejected.
3. Values outside [-1.0, 1.0] are rejected.
4. Signal names and insertion order do not change the result.
5. The output remains in [-1.0, 1.0].
6. The methodology is market-agnostic and contains no provider-specific behavior.
7. It does not produce BUY/SELL/WAIT/NO_TRADE decisions.
8. It owns neither cost, liquidity, slippage nor risk.

## Scope

This methodology is a deterministic composition baseline, not a claim of predictive profitability. More sophisticated combiners may be introduced later only through their own explicit contract, methodology, tests, and evidence.
