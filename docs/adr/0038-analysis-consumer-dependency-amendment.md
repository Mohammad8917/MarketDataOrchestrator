# ADR-0038: Analysis Consumer Dependency Amendment

- Status: Accepted
- Date: 2026-09-30
- Architecture: Frozen v1.0 amendment

## Context

The deterministic regime analysis consumer is an analysis-layer executable vertical slice. Its contract registry and consumer matrix already identify analysis as a downstream consumer of regime and volatility boundaries, but the frozen architecture validator did not permit those two direct dependencies.

This created a concrete contradiction: the intended typed consumer could not pass G04 even though the contract registry explicitly permits the downstream analysis use.

## Decision

Amend the frozen dependency map so the `analysis` layer may depend directly on:

- `regime`
- `volatility`

The existing analysis dependencies remain unchanged. No forbidden dependency is removed, no gate is weakened, and no cycle exception is introduced.

The amendment is valid only if the existing file-level and layer-level cycle checks continue to pass.

## Verification

- G04 architecture dependency validator
- Existing contract and frozen-inventory tests
- Exact-SHA G01-G07 verification

## Consequences

The architecture policy now matches the established contract-consumer direction for deterministic regime analysis and normalized volatility state. The analysis layer can compose those typed boundaries without moving orchestration into another layer or introducing provider, persistence, strategy, decision, or risk dependencies.
