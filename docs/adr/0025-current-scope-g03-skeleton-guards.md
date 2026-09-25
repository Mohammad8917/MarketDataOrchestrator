# ADR-0025 — Current Scope Enforcement for G03 Skeleton Guards

- Status: Accepted
- Date: 2026-09-25
- Extends: ADR 0013 — Phase Plan for Scope-Aware Implementation Completeness
- Related: ADR 0014 — Consumer/Module Binding Before Implementation
- Gate: G03
- Scope: Continuous implementation verification within the declared current vertical slice

## Context

The implementation-phase manifest already classifies the repository inventory, but its initial form placed 355 active skeleton entries under P1. The skeleton guards therefore treated the entire future implementation backlog as the immediate G03 enforcement scope.

That behavior is inconsistent with the dependency-ordered vertical-slice rule in ADR 0013: implementation proceeds by dependency order, and a phase is complete only when that phase's declared scope is closed. The current Batch 4 work is the MarketDataEvent persistence vertical slice, not implementation of the entire repository backlog.

The objective is not to make G03 green by weakening the skeleton rule. The objective is to make the enforced scope explicit and machine-checkable while preserving fail-closed handling of unknown or unclassified skeletons.

## Decision

The authoritative phase manifest gains an explicit `current_scope` object:

- phase: `P1`;
- name: `market_data_persistence_vertical_slice`;
- enforcement: `CURRENT_SCOPE_ONLY`;
- entries:
  - `domain/market_data_event.py`;
  - `persistence/market_data_store.py`;
  - `tests/contract/test_market_data_store.py`.

The two G03 skeleton guards enforce frozen-skeleton completeness only for files in this declared current scope.

The guards continue to enforce all of the following globally:

1. the manifest is valid and versioned;
2. every discovered skeleton has exactly one manifest entry;
3. unknown/unclassified skeletons fail;
4. current-scope entries must be explicitly present, ACTIVE, and assigned to the declared current phase;
5. an ACTIVE skeleton inside the current scope fails G03.

Files outside the current scope are not deleted, ignored from inventory, or reclassified as complete. Their existing phase/status/reason/owner records remain visible in the authoritative manifest as future implementation backlog.

## Non-weakening rule

Current-scope enforcement is not an exemption from implementation completeness. It is the execution boundary for the current vertical slice.

A phase exit still requires closure of all skeletons belonging to that phase before the phase can be declared complete. Advancing `current_scope` is an explicit scope decision and requires fresh evidence from G01 through the applicable gates.

The skeleton marker remains a finding whenever it appears in the enforced scope. The guards must never edit markers, delete tests, suppress paths, or alter the marker definition to obtain PASS.

## Scope transition

Any transition to a new current scope must update the manifest with:

- the new phase;
- an explicit scope name;
- the complete current-scope path set;
- phase/status consistency for every path;
- a dependency/consumer justification;
- fresh G01→applicable-gates evidence.

The next scope must be selected by dependency order and executable consumer evidence, not by arbitrary file count.

## Consequences

- G03 now measures the completeness of the declared current implementation slice rather than pretending that 355 future skeletons are simultaneously being implemented.
- The remaining skeleton backlog remains machine-visible and cannot be mistaken for completed implementation.
- Unknown skeletons remain fail-closed findings.
- The current Batch 4 persistence slice can be verified independently before Group B and later vertical slices are opened.
- When the scope advances, the same guards continue to apply without architectural weakening.

## Evidence

- `docs/compliance/IMPLEMENTATION_PHASE_MANIFEST.json`
- `docs/adr/0013-phase-plan-implementation-completeness.md`
- `tests/architecture/test_no_skeleton_implementation.py`
- `tests/architecture/test_no_skeleton_tests.py`
- Current canonical branch: `audit/fix-known-compliance-gaps`
- Current pre-change baseline: `454804fedee7cf985d24d68ba61ff9025b6802ce`

## Revisit condition

When the current persistence slice is closed and the next dependency-ordered consumer slice is selected, this ADR and the manifest current scope must be reviewed before advancing G03 enforcement.
