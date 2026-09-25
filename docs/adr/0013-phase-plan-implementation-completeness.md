# ADR 0013 — Phase Plan for Scope-Aware Implementation Completeness

- Status: Accepted
- Date: 2026-09-24
- Gate: G03/G07 implementation completeness
- Scope: Production implementation and executable verification skeleton inventory

## Decision

G03 remains fail-closed. Skeleton guards must become scope-aware by reading an explicit, versioned implementation-phase manifest rather than treating every Python file in the repository as an undifferentiated implementation target.

Scope-aware does **not** mean exempt-by-marker. Every excluded file must have a documented owner, reason, contract status, dependency status, and remediation phase. An entry without those fields is a G03 finding.

A file may be excluded from the current implementation phase only when its architectural status is one of:

1. package boundary/module initializer with no runtime behavior;
2. explicitly deferred feature whose contract is not yet active;
3. generated/tooling artifact governed by another verification mechanism;
4. compatibility shim explicitly retained by an accepted ADR.

A production module that owns an active contract, is imported by an active runtime path, or is required by an active gate cannot be excluded merely because implementation is unfinished.

## Phase model

### Phase 0 — Inventory and classification

Deliverables:

- authoritative phase manifest;
- mapping of every skeleton file to a phase/status;
- contract and dependency owner for each active module;
- executable guard that rejects unknown/unclassified files.

Exit condition: zero unclassified skeletons.

### Phase 1 — Core active runtime

Implement the smallest executable vertical slice required by the frozen architecture:

- shared/domain models and active contracts;
- ingestion boundary and provider isolation;
- temporal validation;
- health/state primitives;
- active analysis boundary required by the runtime path.

Verification:

- unit tests;
- contract tests;
- architecture/dependency tests;
- deterministic failure-path tests.

Exit condition: all Phase-1 files have executable behavior and evidence.

### Phase 2 — Analysis capabilities

Implement analysis modules in bounded capability groups:

- derivatives;
- liquidity;
- macro;
- multi-timeframe;
- order flow;
- sentiment.

Each group must have:

- declared input/output contract;
- ownership;
- dependency direction;
- UTC/time semantics where applicable;
- deterministic unit/contract tests;
- no provider implementation leakage.

Exit condition: no active Phase-2 module remains a skeleton.

### Phase 3 — Backtest and historical verification

Implement:

- historical clock;
- replay determinism;
- no-lookahead enforcement;
- signal reproducibility;
- crash/restart and duplicate/replay semantics where applicable.

G07 remains blocked until executable evidence exists.

### Phase 4 — Output and integration

Implement output/notifier paths and full integration pipelines.

Health/status output must consume authoritative runtime state and must not fabricate unavailable fields.

Exit condition: executable integration evidence covers all active pipelines.

### Phase 5 — Release closure

Only after implementation and verification phases are complete:

- G03 completeness;
- G04 architecture/dependency;
- G05 coverage;
- G06 security/supply chain;
- G07 integration/resilience;
- G08 release provenance.

A later phase cannot be used to bypass an earlier mandatory gate.

## Scope-aware guard requirements

The skeleton guards shall:

1. read one authoritative phase manifest;
2. discover skeleton markers;
3. require every discovered file to have exactly one manifest entry;
4. fail on unknown files;
5. fail on duplicate/conflicting entries;
6. fail if an entry claims ACTIVE but remains a skeleton;
7. fail if an excluded/deferred entry lacks an accepted reason and target phase;
8. report the complete classified inventory as machine-readable evidence.

The guard must not edit markers, delete tests, or silently ignore paths.

## Reclassification rule

Changing a file from ACTIVE to DEFERRED/EXCLUDED is an architectural change. It requires:

- manifest update;
- rationale;
- target phase;
- affected contract/dependency review;
- fresh G01→applicable-gates evidence.

The marker itself is never evidence of legitimate deferral.

## Phase execution rule

Implementation proceeds by dependency order, not by arbitrary file count. A phase is complete only when its contracts, dependencies, implementation, and executable verification are all closed.

The objective is not to make the skeleton guard green. The objective is to remove unjustified skeleton state from the active architecture.

## Evidence

The authoritative manifest and scope-aware guards are executable G03 evidence. ADR 0013 documents the governance boundary; it does not substitute for implementation or tests.

## Revisit condition

If the architecture introduces a new runtime layer, contract family, generated-code mechanism, or external plugin boundary, the phase manifest and this ADR must be reviewed before that scope can be considered verified.
