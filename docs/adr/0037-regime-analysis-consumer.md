# ADR-0037: Deterministic Regime Analysis Consumer

- Status: Accepted
- Date: 2026-09-30
- Architecture: Frozen v1.0

## Context

The regime subsystem now provides deterministic feature construction, classification, uncertainty evaluation, and normalized volatility-state boundaries. Those capabilities are individually executable but are not yet exposed as one composition-layer product capability.

## Decision

Define a synchronous, side-effect-free `regime_analysis_boundary` owned by the composition layer.

The evaluator accepts the canonical `RegimeFeatureRequest`, invokes the existing project-owned feature builder, classifier, uncertainty evaluator, and volatility-state evaluator in dependency order, and returns one immutable aggregate output.

The analysis boundary does not perform provider I/O, persistence mutation, strategy selection, trading decisions, risk decisions, or future-data access.

The aggregate preserves the original `event_time`, `received_at`, and `source_event_id` across all components. The normalized uncertainty value remains the confidence-complement baseline and is not a probability or calibrated statistical measure.

## Boundary rules

- synchronous and deterministic;
- side-effect-free;
- consumes only the observations admitted by `RegimeFeatureRequest`;
- reuses existing lower-layer contracts rather than duplicating their methodology;
- preserves source-event provenance;
- invalid lower-layer requests fail through the existing typed contracts.

## Versioning

- Contract ID: `regime_analysis_boundary`
- Contract version: `1.0.0`
- Methodology ID: `deterministic_regime_analysis_baseline`
- Methodology version: `1.0.0`

Changing aggregation semantics, provenance, temporal behavior, or lower-layer interpretation requires a new contract/methodology version and ADR.

## Verification

- `tests/contract/test_regime_analysis.py`
- G01-G07 and mutation testing

## Consequences

The project now has an executable composition-layer vertical slice without coupling analysis to providers, strategy, risk, or orchestration. Future analysis capabilities can consume the typed aggregate without reconstructing lower-layer results independently.
