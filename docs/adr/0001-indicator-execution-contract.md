# ADR-0001: Canonical Indicator Execution Contract

- Status: Accepted
- Date: 2026-09-24
- Architecture: Frozen v1.0

## Context

The indicator subsystem contained only skeleton implementations and no typed contract binding. This left the indicator boundary unverifiable and allowed future concrete indicators to invent incompatible input/output shapes.

## Decision

Define one canonical protocol-only indicator contract at `indicators/core/base.py`:

- `IndicatorRequest` carries named numeric series, source event identity, event time, and receipt time.
- Boundary timestamps MUST be timezone-aware UTC.
- `IndicatorOutput` carries named numeric results, the source event time, indicator identity, and contract version.
- Concrete indicators implement `Indicator.calculate(IndicatorRequest) -> IndicatorOutput`.
- The contract is synchronous and pure in the sense that indicator execution performs no provider or external I/O.
- Contract identity is `indicator_execution_boundary` version `1.0.0`.

The Contract Registry in `docs/contracts.md` is the only registry entry for this boundary. Contract tests and a single-source architecture test provide executable verification.

## Consequences

Concrete indicator algorithms can be implemented independently without inventing new boundary types. Temporal semantics are explicit at the indicator boundary. Provider and higher-layer concerns remain outside the indicator subsystem.

This decision does not implement the 69 concrete indicator algorithms; those remain separate implementation work and cannot be treated as released behavior until their contract and coverage gates pass.

## Verification

- `tests/contract/test_indicator_contract.py`
- `tests/architecture/test_indicator_single_source.py`
- Architecture/dependency validator
