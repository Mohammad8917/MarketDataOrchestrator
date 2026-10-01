# ADR 0013 — Deterministic Multi-Timeframe Structure Alignment v1

- Status: Accepted
- Date: 2026-10-01
- Scope: Market Structure → Multi-Timeframe Structure
- Markets: Crypto, Forex, Gold
- Contract: `mtf_structure_alignment_boundary` v1.0.0
- Methodology: `deterministic_latest_point_alignment` v1.0.0

## Decision

Multi-timeframe structure is a descriptive analytical layer that consumes already-evaluated point-in-time Market Structure outputs. It does not re-detect swings and does not own market-data access.

For each named timeframe:

- The latest confirmed structural point is selected by event time.
- HH/HL maps to `bullish`.
- LH/LL maps to `bearish`.
- No point maps to `unknown`.
- Conflicting structural kinds at the same latest timestamp map to `unknown`; the methodology never guesses.

Across timeframes:

- only bullish known observations → `bullish`
- only bearish known observations → `bearish`
- both bullish and bearish known observations → `mixed`
- no known directional observations → `insufficient`

Unknown observations do not override known directional observations.

## Boundaries

The output is structural evidence, not a trading action, recommendation, risk result, cost result, or decision. Provider I/O and persistence remain outside the layer.

## Point-in-time invariant

Every input Market Structure observation must have an event time no later than the MTF request event time. Future observations are rejected by the contract.

## Rationale

This creates an explicit, deterministic, auditable MTF layer without inventing probabilistic confidence or implicit trading semantics. The same contract can be used for Crypto, Forex, and Gold because it depends only on canonical Market Structure outputs.
