# ADR 0006 — Deterministic Confirmation Methodology v1

- Status: Accepted
- Date: 2026-10-01
- Architecture: Frozen v1.0

## Decision

Introduce `deterministic_directional_consensus_v1` version `1.0.0` as the first executable confirmation methodology.

The methodology treats each normalized analytical signal as a directional vote:
- positive values vote positive;
- negative values vote negative;
- zero values are neutral.

The score is:

`(positive_votes - negative_votes) / total_signals`

The result is confirmed when `abs(score) >= 0.5`.

## Scope

The methodology is market-agnostic and applies equally to Crypto, Forex, and Gold.

It consumes only normalized analytical evidence through `ConfirmationRequest`. It does not inspect market data, provider identity, timeframe, execution conditions, liquidity, cost, risk, or decision semantics.

A confirmed output is an analytical confirmation state only. It is not a BUY/SELL instruction and is not evidence of profitability.

## Consequences

- Behavior is deterministic and replayable.
- Equal directional voting avoids hidden market-specific weighting.
- Neutral evidence reduces confirmation strength without creating a directional vote.
- Methodology parameters are explicit and versioned.
- Future methodologies may replace or complement this baseline without changing the v1 confirmation contract.

## Verification

The methodology is covered by strong unit tests for:
- positive, negative, mixed, tie, and neutral evidence;
- threshold behavior;
- invalid and non-finite values;
- deterministic provenance-bound confirmation identifiers.
