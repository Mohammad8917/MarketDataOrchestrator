# FILE: docs/adr/0008-integration-and-resilience-gate.md
# KIT: Architecture & Implementation Compliance Kit
# FILE_VERSION: 1.0.0
# DATE_GREGORIAN: 2026-09-24
# DATE_PERSIAN: 1405-07-02
# AUTHOR: محمد حسن زاده
# RESPONSIBILITY: Record the decision to fail closed until executable integration and resilience evidence exists.
# LAYER: architecture-record
# OWNS: Integration/resilience gate decision record.
# DOES_NOT_OWN: Runtime integration implementation, provider capability claims, or release approval.
# DEPENDENCIES: docs/runbooks.md; tests/integration; tests/backtest; tests/regression
# PYTHON: N/A
# LICENSE: Proprietary — All Rights Reserved
# NOTICE: Unauthorized use prohibited without written authorization
# COMPLIANCE: Architecture & Implementation Compliance Kit v1.0

# ADR-0008: Integration and Resilience Gate

## Status

Accepted — release-blocking until executable evidence exists.

## Context

The compliance kit requires automated integration/resilience verification and operational runbooks. The repository currently contains the integration, backtest, and regression test locations, but the relevant test modules are frozen skeletons and do not execute behavioral verification.

## Decision

G07 remains fail-closed. The CI gate must execute the integration, backtest, and regression suites and treat zero collected tests as failure. No placeholder test, forced exit code, coverage exclusion, or documentation-only assertion may be used to turn the gate green.

Executable evidence must cover, as applicable:

- cross-boundary pipeline behavior;
- provider failure isolation;
- retry/rate-limit behavior;
- temporal/replay invariants;
- crash/restart and duplicate handling;
- deterministic historical replay;
- regression protection.

## Consequence

The branch cannot be classified release-ready until production pipeline contracts are implemented and the corresponding integration/resilience tests execute successfully. This preserves the fail-closed rule instead of converting missing evidence into PASS.
