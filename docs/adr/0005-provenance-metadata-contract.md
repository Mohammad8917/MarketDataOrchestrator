# ADR-0005: Canonical Provenance Metadata Contract

- Status: Accepted
- Date: 2026-09-24
- Architecture: Frozen v1.0

## Decision

The provenance_metadata contract is the single canonical contract for source traceability at the shared boundary.

It requires a non-empty source event identity, source identifier, explicit UTC observed and received timestamps, a non-empty content digest, and an explicit contract version. The model is immutable and performs no I/O.

## Ownership

The shared boundary owns the data shape and validation invariants. Evidence algorithms remain separately owned by the evidence subsystem. Provider connectors, persistence, decision, and risk components do not own provenance semantics.

## Release rule

Concrete evidence behavior is not released merely because an implementation file exists. It must bind to the canonical provenance contract and satisfy applicable architecture, contract, coverage, security, temporal, and release gates.
