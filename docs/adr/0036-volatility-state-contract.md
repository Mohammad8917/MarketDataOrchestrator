# ADR-0036: Volatility State Contract

- Status: Accepted
- Date: 2026-09-30
- Architecture: Frozen v1.0

## Context

The regime subsystem now exposes a deterministic normalized volatility score, but no independent typed boundary exists for a downstream volatility-state capability. A separate contract is required before implementation or strategy consumption.

## Decision

Define a synchronous, side-effect-free `volatility_state_boundary`.

The boundary receives a normalized volatility score from the project-owned regime feature methodology and maps it to a canonical bounded state representation without introducing external thresholds, provider I/O, persistence mutation, strategy/risk decisions, or probabilistic semantics.

The initial contract deliberately defines the normalized score and provenance boundary only. Classification thresholds and adaptive methods are not part of this contract and must be introduced through a separate versioned methodology contract.

### Inputs

`VolatilityStateRequest` MUST contain:
- `volatility_score`: finite numeric value in [-1, 1];
- `event_time`: timezone-aware UTC;
- `received_at`: timezone-aware UTC;
- `source_event_id`: non-empty provenance identity.

### Outputs

`VolatilityStateOutput` MUST contain:
- `volatility_score`;
- `event_time`;
- `source_event_id`;
- contract version.

The score preserves the existing semantics from ADR-0034: positive means higher short-window volatility than the long-window baseline; negative means lower; zero means equal or no movement.

This contract does not define labels such as low/medium/high, fixed thresholds, or trading implications.

## Boundary rules

The evaluator is synchronous, deterministic, side-effect-free, and performs no provider/external I/O, persistence mutation, strategy selection, trading decision, or risk decision. It does not consume future observations and preserves provenance.

Invalid score, timestamp, or provenance fields MUST fail deterministically with `ValueError`.

## Versioning

- Contract ID: `volatility_state_boundary`
- Contract version: `1.0.0`
- Methodology ID: `normalized_regime_volatility_passthrough`
- Methodology version: `1.0.0`

Changing score semantics, bounds, provenance, or temporal rules requires a new contract/methodology version and ADR.

## Consequences

The project obtains an explicit volatility-state boundary without inventing market thresholds. Future thresholded, percentile, ATR, multi-timeframe, adaptive, probabilistic, or ML volatility methodologies can be added independently.
