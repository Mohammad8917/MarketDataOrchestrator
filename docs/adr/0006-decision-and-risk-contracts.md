# ADR-0006: Decision and Risk Boundary Contracts

- Status: Accepted
- Date: 2026-09-24
- Architecture: Frozen v1.0

## Decision

Decision and risk each expose one canonical typed boundary. Decision evaluates actionable intent; risk evaluates the permitted exposure envelope. Neither contract owns provider I/O or persistence mutation.

## Contracts

- decision_evaluation_boundary v1.0.0
- risk_evaluation_boundary v1.0.0

Both require explicit UTC event/receipt semantics, source event identity, immutable outputs, and bounded normalized values.

## Ownership

Concrete decision logic remains under decision/. Concrete risk logic remains under risk/. The shared contract model is not permission for either subsystem to bypass the other subsystem's ownership.

## Release rule

Concrete behavior is not released merely because implementation files exist. Contract binding, architecture direction, coverage, security, temporal integrity, and release gates remain mandatory.
