# ADR 0023 — Lineage Reconciliation

- Status: Accepted
- Date: 2026-09-25
- Scope: Reconciliation of the divergent `main` and `audit/fix-known-compliance-gaps` lineages

## Executive Summary

- Two branches diverged: `main` is 59 commits ahead of the merge-base and `audit/fix-known-compliance-gaps` is 339 commits ahead.
- Five ADR number collisions were identified and resolved through a unified namespace.
- `audit/fix-known-compliance-gaps` becomes the canonical continuation branch after reconciliation; `main` is retained as archived.
- Main runtime artifacts are preserved; audit compliance artifacts remain authoritative where they are stronger or complementary.
- Cherry-pick is selective: not all 59 main commits are copied.
- Reconciliation completes only when the reconciled SHA passes G01–G04.

## Context

The repository contains two divergent development lineages. Neither branch is an ancestor of the other. The main lineage contains the more complete runtime vertical slice, including MarketDataStore, BacktestEngine, EquityCurve output contracts, HANDOFF, and runtime-oriented ADRs. The audit lineage contains the compliance-oriented implementation and evidence work, including G03 consumer/contract governance, G04 validation, skeleton guards, indicator implementations, evidence artifacts, and the Bollinger oracle correction.

The reconciliation work identified both non-overlapping artifacts and semantic/namespace collisions. A blind merge or blind cherry-pick would obscure provenance and could reintroduce superseded or conflicting decisions.

## Decision

Reconcile the two lineages under one authoritative architectural namespace.

### ADR namespace

- ADR-0001 through ADR-0012 remain unchanged.
- ADR-0013: Phase Plan + Scope-Aware Implementation Completeness.
- ADR-0014: Consumer/Module Binding Before Implementation.
- ADR-0015: Evidence Artifact Lifecycle.
- ADR-0016: G04 Gate Independence.
- ADR-0017: Runtime Consumer Definition.
- ADR-0018: Registry Boundary Aggregation.
- ADR-0019: Test Oracle.
- ADR-0020: SQLite Event Persistence.
- ADR-0021: Output Contract / Runtime Direction.
- ADR-0022: Terminal Registry Extension.
- ADR-0023: Lineage Reconciliation.
- ADR-0024: Concurrent Development Policy.

The main and audit ADRs numbered 0013 and 0014 are semantically reconciled rather than treated as competing decisions. Their distinct rules are preserved within the unified ADRs.

ADR-0015, ADR-0016, and ADR-0017 retain their audit semantics as independent cross-cutting governance decisions. Main ADRs originally numbered 0015–0017 are renumbered to ADR-0020–0022 without changing their substantive decisions.

### Artifact reconciliation

The reconciliation classification is:

- `equivalent`: retain one canonical representation.
- `complementary`: retain both compatible artifacts.
- `superseded`: retain the newer/better-supported artifact.
- `conflicting`: resolve explicitly before adoption; do not overwrite blindly.

The main runtime vertical slice is preserved where it supplies executable artifacts absent from audit. Audit compliance and evidence artifacts are preserved where they provide the authoritative compliance implementation or stronger governance.

The reconciled architecture MUST preserve evidence provenance and MUST NOT claim that a future consumer is a current runtime consumer.

### Cherry-pick policy

Not all main commits are cherry-picked.

Each main commit is classified as exactly one of:

- `required`: implements an artifact that is required by the reconciliation scope and is not otherwise present.
- `superseded`: audit already contains an equivalent or better-supported implementation or decision.
- `redundant`: the change is already represented in the audit lineage.
- `conflicting`: the change overlaps a semantic conflict and requires manual reconciliation.

Only `required` commits are eligible for cherry-pick.

`conflicting` commits MUST be resolved manually at the artifact/decision level. Git merge MUST NOT be used as a substitute for architectural reconciliation. A commit that contains both required and conflicting changes MUST be decomposed or manually recreated rather than blindly cherry-picked.

### Branch disposition

After reconciliation completes and the reconciled SHA passes G01–G04:

- `audit/fix-known-compliance-gaps` becomes the canonical branch.
- New work continues on `audit/fix-known-compliance-gaps`.
- `main` is retained as archived historical lineage.
- No new independent architectural work is started on the archived `main`.

### Evidence and baseline

Every reconciled claim remains SHA-bound. A green gate on an intermediate SHA is not treated as evidence for a later SHA.

The current baseline remains a partial freeze until reconciliation is complete. No implementation work is authorized merely because an artifact exists on one branch.

## Consequences

- Runtime completeness from main is not discarded.
- Compliance maturity from audit is not discarded.
- Provenance remains inspectable at commit level.
- The final branch has one ADR namespace rather than competing numeric namespaces.
- Selective cherry-pick requires a commit-level reconciliation matrix before execution.
- CI evidence must be regenerated after the reconciled SHA is created.

## Completion Criteria

Reconciliation is complete only when all of the following hold:

1. ADR namespace is reconciled.
2. Required main commits have been explicitly classified and transferred.
3. Conflicting artifacts are manually reconciled.
4. `docs/contracts.md`, CI workflow, architecture validator, and indicator implementations have a single authoritative form.
5. Gap Register is updated from the reconciled state.
6. The reconciled SHA passes G01–G04.
7. The resulting SHA is recorded as the new baseline.
8. `audit/fix-known-compliance-gaps` is the canonical continuation branch and `main` is retained as archived.

## Explicit Constraint

Until the completion criteria above are satisfied:

**NO MERGE · NO BLIND CHERRY-PICK · NO IMPLEMENTATION COMMIT AS RECONCILIATION COMPLETION**
