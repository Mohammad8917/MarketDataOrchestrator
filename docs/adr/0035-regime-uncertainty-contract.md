# ADR-0035: Regime Uncertainty Contract

- Status: Accepted
- Date: 2026-09-30
- Architecture: Frozen v1.0

## Context

The regime subsystem now has a canonical classification boundary and a deterministic feature methodology. The classifier exposes a bounded confidence value, but no independent contract defines how uncertainty is represented and propagated.

A separate boundary is required before uncertainty-aware consumers are implemented. The boundary must not silently introduce probabilistic semantics, trading decisions, or risk policy.

## Decision

Define a synchronous, side-effect-free regime_uncertainty_boundary.

The baseline contract represents uncertainty as the complement of canonical bounded regime confidence:

uncertainty_score = 1 - confidence

This is a normalized uncertainty indicator, not a probability, posterior belief, calibration measure, or statistical confidence interval.

### Inputs

RegimeUncertaintyRequest MUST contain:

- confidence: numeric, finite, within [0, 1];
- event_time: timezone-aware UTC;
- received_at: timezone-aware UTC;
- source_event_id: non-empty provenance identity.

### Outputs

RegimeUncertaintyOutput MUST contain:

- uncertainty_score: finite, within [0, 1];
- event_time;
- source_event_id;
- contract version.

For the baseline mapping:

- confidence 1.0 produces uncertainty 0.0;
- confidence 0.0 produces uncertainty 1.0;
- intermediate values are transformed deterministically by 1 - confidence.

### Boundary rules

The evaluator:

- is synchronous;
- performs no provider or external I/O;
- performs no persistence mutation;
- performs no strategy selection;
- performs no trading decision;
- performs no risk decision;
- does not consume future observations;
- preserves source event provenance.

Invalid confidence values and invalid temporal/provenance fields MUST fail deterministically with ValueError.

## Versioning

- Contract ID: regime_uncertainty_boundary
- Contract version: 1.0.0
- Baseline mapping ID: confidence_complement_baseline
- Baseline mapping version: 1.0.0

Changing the mapping semantics, bounds, provenance, or temporal rules requires a new contract/methodology version and ADR.

## Consequences

Uncertainty becomes an explicit typed boundary between regime classification and future uncertainty-aware consumers. Downstream components may consume the normalized uncertainty indicator without treating it as a calibrated probability.

No strategy, risk, sizing, or execution behavior is implied by this contract.
