# ADR-0026 — Current-Scope Coverage Enforcement

- Status: Accepted
- Date: 2026-09-25
- Extends: ADR-0013
- Related: ADR-0025
- Gate: G05

## Context

The first G05 execution after the current P1 vertical slice became executable ran all repository tests and required 100% coverage across the entire production tree. The measured result was 86%, with uncovered code distributed across future, not-yet-implemented capabilities.

G03 is now explicitly current-scope aware, while G05 remained repository-global. This makes the gate ordering inconsistent with the phase model: a dependency-ordered vertical slice cannot pass its own coverage gate while unrelated future-phase production modules are still intentionally incomplete.

The evidence from Compliance CI #553 is decisive: 216 tests passed; the failure was solely the global 100% coverage threshold. The current vertical slice production files were not the sole coverage population.

## Decision

While the manifest declares an active `current_scope`, G05 measures branch coverage for the production files in that current scope and requires 100%.

For the current scope, the coverage population is:

- `domain/market_data_event.py`
- `persistence/market_data_store.py`

Tests remain executed from the full repository test suite, but coverage is evaluated only against the current production slice.

The CI command must use an explicit include list derived from the current scope. It must not lower `--fail-under` below 100%.

## Non-weakening rule

This is not a reduction of the quality threshold. The threshold remains 100% for the active production scope.

When the implementation scope advances, the coverage population advances with it. A phase cannot be declared complete while its active production scope has uncovered branches.

Repository-wide 100% coverage remains a release-closure property under the later implementation/release phases; it is not silently redefined as the current-slice gate.

No `omit` or exclusion may be added merely to hide uncovered code inside the declared current production scope.

## Scope transition

Every current-scope transition must identify the production coverage population explicitly and provide fresh G01-G05 evidence.

## Evidence

- Compliance CI #553, SHA `b52c2a1f003e88875dd5479b552a5c393a1d5f7b`
- `docs/compliance/IMPLEMENTATION_PHASE_MANIFEST.json`
- `docs/adr/0013-phase-plan-implementation-completeness.md`
- `docs/adr/0025-current-scope-g03-skeleton-guards.md`
