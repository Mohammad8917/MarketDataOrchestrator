# ADR 0024 — Concurrent Development Policy

- Status: Accepted
- Date: 2026-09-25
- Scope: Branch coordination and prevention of silent architectural divergence

## Context

The repository developed two divergent lineages containing complementary artifacts, semantic conflicts, and ADR namespace collisions. The observed condition is branch divergence; this ADR does not attribute that divergence to any particular person, agent, or process failure.

Without an explicit coordination policy, parallel changes can create competing contracts, duplicate implementations, stale evidence, and incompatible architectural decisions.

## Decision

All concurrent development MUST follow an explicit reconciliation protocol.

### 1. Verify the canonical state

Before changing architecture or contracts, identify:

- the intended working branch;
- the current HEAD SHA;
- the applicable baseline;
- the latest verified CI evidence.

### 2. Read the operational handoff

`HANDOFF.md` is the operational source of truth for the current vertical slice, active constraints, dependencies, and immediate next step.

If HANDOFF conflicts with an architectural decision, the ADR is authoritative for architecture and HANDOFF MUST be updated.

### 3. Identify phase and scope

Every change MUST identify:

- current phase;
- artifact scope;
- relevant contracts;
- relevant consumers;
- relevant gates;
- dependencies on other active work.

No new module enters scope without consumer evidence.

### 4. Declare divergence

When work is intentionally developed on a different branch, the branch scope and expected reconciliation point MUST be explicit.

Silent independent architectural lineages are not permitted.

### 5. Classify before integrating

Every divergent artifact MUST be classified as:

- `equivalent`;
- `complementary`;
- `superseded`; or
- `conflicting`.

Integration MUST follow that classification rather than branch order alone.

### 6. Preserve evidence provenance

Evidence is SHA-bound. A result produced on one SHA MUST NOT be represented as evidence for another SHA unless the same result is independently verified for that SHA.

### 7. Coordinate contracts before implementation

Contract changes, consumer bindings, registry changes, and architecture-policy changes MUST be reconciled before dependent implementation proceeds.

Consumer evidence precedes contract binding, and contract binding precedes implementation where the applicable governance rules require that order.

### 8. No silent architectural overwrite

A branch MUST NOT silently replace another branch's contract, validator, CI policy, or ADR decision. Conflicts require an explicit decision record or an already-authoritative reconciliation decision.

## Operational Handoff Requirements

At each handoff, the active branch SHOULD record:

- current SHA;
- gate state;
- known failures;
- active GAPs;
- files in scope;
- files explicitly out of scope;
- next approved action;
- constraints such as NO MERGE, NO CHERRY-PICK, or NO COMMIT.

The handoff MUST distinguish observed facts from planned work.

## Current Reconciliation Trigger

The current trigger for this policy is the observed divergence between `main` and `audit/fix-known-compliance-gaps`. The policy is applied without inferring a human or agent cause for that divergence.

## Consequences

- Parallel work remains possible when scope is explicit.
- Architectural state remains auditable.
- Evidence cannot silently drift across SHAs.
- Reconciliation becomes a controlled artifact-by-artifact process rather than an implicit branch merge.
- Future divergence is surfaced early through HANDOFF, ADR, contract, consumer, and gate references.

## Revisit Condition

Revisit this ADR if the repository adopts a different branch governance model or an automated mechanism that provides equivalent guarantees for scope declaration, provenance, and architectural reconciliation.
