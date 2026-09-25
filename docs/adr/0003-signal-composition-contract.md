# ADR-0003: Canonical Signal Composition Contract

- Status: Accepted
- Date: 2026-09-24
- Architecture: Frozen v1.0

## Context

The composition subsystem contained combiners and related boundaries as skeletons but had no typed contract binding for the composition output. This left composition behavior structurally present but contractually unverifiable.

## Decision

Define one canonical signal composition contract at `composition/composer.py`:

- `CompositionRequest` carries named upstream signals, source event identity, event time, and receipt time.
- Boundary timestamps MUST be timezone-aware UTC.
- `CompositionOutput` carries the composed value, source event time, composition identity, and contract version.
- Concrete composers implement `SignalComposer.compose(CompositionRequest) -> CompositionOutput`.
- The contract is synchronous and performs no provider or external I/O.
- The contract excludes persistence mutation, decision finalization, and risk ownership.
- Contract identity is `signal_composition_boundary` version `1.0.0`.

The Contract Registry in `docs/contracts.md` is the only registry entry for this boundary. Contract tests and a single-source architecture test provide executable verification.

## Consequences

Future combiners can be implemented independently without inventing incompatible boundary types. Temporal provenance is explicit at the composition boundary.

This decision does not implement concrete combiners, confirmation, correlation, divergence, or preset behavior; those remain separate implementation work and cannot be treated as released behavior until their contracts and coverage gates pass.

## Verification

- `tests/contract/test_composition_contract.py`
- `tests/architecture/test_composition_single_source.py`
- Architecture/dependency validator
