# PROJECT_STATE.md

> AUTO-GENERATED. DO NOT EDIT.
> Generated: 2026-09-25 11:23 UTC
> Source: git log + evidence/ + docs/adr/

---

## 1. Current State

- Branch: audit/fix-known-compliance-gaps
- SHA: 3bb2dcb5a51593e06204ab066c70ebf54cd3a391
- Short: 3bb2dcb
- Last commit: docs: bind milestone claims to protected CI evidence
- Date: 2026-09-25 14:51:40 +0330
- Phase (auto): Unknown

## 2. Gate Status

- G01: PENDING
- G02: PENDING
- G03: PENDING
- G04: PENDING
- G05: PENDING
- G06: PENDING
- G07: PENDING

## 3. ADR Index

- 0001-indicator-execution-contract.md — ADR-0001: Canonical Indicator Execution Contract
- 0002-regime-classification-contract.md — ADR-0002: Canonical Regime Classification Contract
- 0003-signal-composition-contract.md — ADR-0003: Canonical Signal Composition Contract
- 0004-strategy-evaluation-contract.md — ADR-0004: Canonical Strategy Evaluation Contract
- 0005-provenance-metadata-contract.md — ADR-0005: Canonical Provenance Metadata Contract
- 0006-decision-and-risk-contracts.md — ADR-0006: Decision and Risk Boundary Contracts
- 0007-temporal-integrity-boundary.md — ADR-0007: Temporal Integrity Boundary
- 0008-integration-and-resilience-gate.md — FILE: docs/adr/0008-integration-and-resilience-gate.md
- 0009-frozen-contract-reverse-guards.md — ADR 0009 — G03 Reverse/Static Guard Coverage for Frozen Contracts
- 0010-g06-transitive-dependency-reproducibility.md — ADR 0010 — G06 Transitive Dependency Reproducibility
- 0011-g01-ruff-baseline.md — ADR 0011 — G01 Ruff Baseline
- 0012-workflow-placeholder-policy.md — ADR 0012 — Workflow Placeholder Policy
- 0013-phase-plan-implementation-completeness.md — ADR 0013 — Phase Plan for Scope-Aware Implementation Completeness
- 0014-module-export-consumer-binding.md — ADR 0014 — Module Export and Consumer Binding Before Implementation
- 0015-evidence-artifact-lifecycle.md — ADR 0015 — Evidence Artifact Lifecycle
- 0016-g04-gate-independence.md — ADR 0016 — G04 Architecture Gate Independence
- 0017-runtime-consumer-definition.md — ADR 0017 — Runtime Consumer Definition
- 0018-registry-boundary-aggregation.md — ADR 0018 — Registry Boundary Aggregation of Frozen Types
- 0019-partial-freeze-baseline.md — ADR 0019 — Partial Freeze Baseline
- 0020-partial-freeze-extension.md — ADR 0020 — Partial Freeze Extension After Indicator and Registry Milestone
- 0025-current-scope-g03-skeleton-guards.md — ADR-0025 — Current Scope Enforcement for G03 Skeleton Guards
- 0026-current-scope-coverage.md — ADR-0026 — Current-Scope Coverage Enforcement
- 0027-bandit-suppression-policy.md — ADR-0027 — Bandit Suppression Policy
- ADR-001-indicator-location.md — ADR-001-indicator-location
- ADR-002-validator-ownership.md — ADR-002-validator-ownership
- ADR-0023-lineage-reconciliation.md — ADR 0023 — Lineage Reconciliation
- ADR-0024-concurrent-development-policy.md — ADR 0024 — Concurrent Development Policy
- ADR-003-domain-vs-adapters.md — ADR-003-domain-vs-adapters
- ADR-004-forex-gold-status.md — ADR-004-forex-gold-status
- ADR-005-execution-simulator.md — ADR-005-execution-simulator
- ADR-006-strategy-layer.md — ADR-006-strategy-layer
- ADR-007-regime-location.md — ADR-007-regime-location
- ADR-008-pipeline-contracts.md — ADR-008-pipeline-contracts
- ADR-TEST-ORACLE.md — ADR-TEST-ORACLE — Expected-value derivation in tests

## 4. Open Gaps

- GAP-014 — Bollinger mocked-band expected-value provenance
- GAP-022 — Main/audit architecture validator fix divergence
- GAP-008 — MarketDataStore orphan

## 5. Recent SHA History (auto)

- 3bb2dcb5 — UNKNOWN — 2026-09-25 — docs: bind milestone claims to protected CI evidence
- 4308ec3a — UNKNOWN — 2026-09-25 — chore: auto-update project state [skip ci]
- 26714e17 — UNKNOWN — 2026-09-25 — docs: update handoff and gap register after vertical slice
- 36d38a83 — UNKNOWN — 2026-09-25 — docs: update handoff and gap register after vertical slice
- 4c9f94a6 — UNKNOWN — 2026-09-25 — chore: auto-update project state [skip ci]
- a19078c0 — UNKNOWN — 2026-09-25 — style: restore test spacing
- 86afbeb7 — UNKNOWN — 2026-09-25 — style: format backtest integration tests
- 487fd036 — UNKNOWN — 2026-09-25 — chore: auto-update project state [skip ci]
- f78ace29 — FAIL — 2026-09-25 — fix: type EquityCurve invariant tests
- bfab75ce — UNKNOWN — 2026-09-25 — chore: auto-update project state [skip ci]
- 144d2cfa — FAIL — 2026-09-25 — test: cover EquityCurve invariants
- edc3bdbf — UNKNOWN — 2026-09-25 — chore: auto-update project state [skip ci]
- 47bf1717 — FAIL — 2026-09-25 — test: correct Decimal drawdown oracle
- bffddc99 — UNKNOWN — 2026-09-25 — chore: auto-update project state [skip ci]
- 44367eea — FAIL — 2026-09-25 — fix: reconcile backtest domain dependency policy

## 6. Interface Chain

```
## Initial contract baseline

| contract_id | owner_layer | status | verification |
|---|---|---|---|
| ingestion_provider_boundary | ingestion | ACTIVE | G04_ARCHITECTURE_DEPENDENCY |
| market_data_event | domain | ACTIVE | G03_UNIT_CONTRACT |
| provenance_metadata | shared | ACTIVE | G03_UNIT_CONTRACT |
| temporal_event_boundary | temporal | ACTIVE | G07_INTEGRATION_RESILIENCE |
| validation_result | validation | ACTIVE | G03_UNIT_CONTRACT |
| indicator_execution_boundary | indicators | ACTIVE
```

## 7. Auto Notes

## Recent Commits (auto)
- docs: bind milestone claims to protected CI evidence
- chore: auto-update project state [skip ci]
- docs: update handoff and gap register after vertical slice
- docs: update handoff and gap register after vertical slice
- chore: auto-update project state [skip ci]

## Recent ADRs (auto)
- ADR-004-forex-gold-status
- ADR-007-regime-location
- ADR-006-strategy-layer
- ADR-002-validator-ownership
- ADR-003-domain-vs-adapters

---

## 8. Instructions for New Chat

1. Read this file completely.
2. Answer these 5 questions BEFORE proposing anything:
   - What branch and SHA?
   - What is the gate status?
   - What are 3 open findings?
   - What are 3 next steps?
   - What is the interface chain?
3. Do NOT propose until answered.

## 9. Locked Principles

1. README locked.
2. No artificial green gates.
3. Every new SHA restarts G01.
4. Every claim needs machine evidence.
5. Fail-closed: red gate = stop.
6. Consumer before contract (ADR-0014).
7. Interface-First (ADR-0014).
8. Vertical slice before horizontal.
9. No artificial implementation.
