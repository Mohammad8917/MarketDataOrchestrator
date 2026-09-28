# PROJECT_STATE.md

> AUTO-GENERATED. DO NOT EDIT.
> Generated: 2026-09-28 09:17 UTC
> Source: git log + evidence/ + docs/adr/

---

## 1. Current State

- Branch: main
- SHA: 82ed01e02b6fbd4ad923289b8c5cc67b5bc386b0
- Short: 82ed01e
- Last commit: Merge pull request #6 from Mohammad8917/fix/auto-state-workflow-run-noop
- Date: 2026-09-28 12:45:09 +0330
- Phase (auto): Reconciliation

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
- 0029-public-repository-surface-and-license.md — ADR-0029 — Public Repository Surface and License Boundary
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
- ADR-009-architecture-validator-same-layer-imports.md — ADR-009: Same-Layer Imports in Architecture Validation
- ADR-010-deterministic-market-event-identity.md — ADR-010: Deterministic Canonical Market Event Identity
- ADR-011-temporal-event-boundary.md — ADR-011: Temporal Event Boundary
- ADR-012-contract-consumer-before-implementation.md — ADR-012: Consumer Before Contract Implementation
- ADR-013-phase-contract-verification-plan.md — ADR-013: Contract Verification Phase Plan
- ADR-014-executable-consumer-before-verification.md — ADR-014 — Executable Consumer Before Contract Verification
- ADR-015-sqlite-event-persistence-semantics.md — ADR-015: SQLite Event Identity, Replay Conflict, and Exact Numeric Persistence
- ADR-016-output-contract-and-runtime-direction.md — ADR-016: Output Contract and Runtime Direction
- ADR-017-terminal-contract-registry-extension.md — ADR-017: Terminal Output Registry Extension and Backtest Domain Boundary
- ADR-TEST-ORACLE.md — ADR-TEST-ORACLE — Expected-value derivation in tests

## 4. Open Gaps

- GAP-014 — Bollinger mocked-band expected-value provenance
- GAP-022 — Main/audit architecture validator fix divergence
- GAP-008 — MarketDataStore orphan

## 5. Recent SHA History (auto)

- 82ed01e0 — UNKNOWN — 2026-09-28 — Merge pull request #6 from Mohammad8917/fix/auto-state-workflow-run-noop
- d95cf742 — UNKNOWN — 2026-09-28 — fix: make Auto State workflow_run success-only and no-op safe
- c376c0a5 — UNKNOWN — 2026-09-28 — chore: auto-update project state [skip ci]
- 7875fa18 — UNKNOWN — 2026-09-28 — Merge pull request #5 from Mohammad8917/audit/fix-known-compliance-gaps
- 77d71d3e — UNKNOWN — 2026-09-28 — fix: remove duplicate dependency audit command
- d5f8cb22 — UNKNOWN — 2026-09-28 — fix: format canonical ingestion temporal contract tests
- b41f995f — UNKNOWN — 2026-09-28 — merge: reconcile main with canonical audit contracts
- 49645a19 — UNKNOWN — 2026-09-27 — fix: validate event identity fields before UUID derivation
- df6cac74 — UNKNOWN — 2026-09-27 — test: assert drawdown using canonical Decimal formula
- 951d6044 — UNKNOWN — 2026-09-27 — test: keep benchmark OHLC fixtures canonical
- 1c9ff9bc — UNKNOWN — 2026-09-27 — fix: align temporal replay fixture with timeframe contract
- 6be29eea — UNKNOWN — 2026-09-27 — fix: restore canonical architecture header for provider boundary
- dbe13a57 — UNKNOWN — 2026-09-27 — fix: synchronize G03 reconciliation evidence
- ac6c2e31 — UNKNOWN — 2026-09-27 — fix: restore complete contract registry bindings
- 02156fc2 — UNKNOWN — 2026-09-27 — test: make regression fixture strict-mypy compatible

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
- Merge pull request #6 from Mohammad8917/fix/auto-state-workflow-run-noop
- fix: make Auto State workflow_run success-only and no-op safe
- chore: auto-update project state [skip ci]
- Merge pull request #5 from Mohammad8917/audit/fix-known-compliance-gaps
- fix: remove duplicate dependency audit command

## Recent ADRs (auto)
- ADR-004-forex-gold-status
- ADR-015-sqlite-event-persistence-semantics
- ADR-007-regime-location
- 0016-g04-gate-independence
- 0018-registry-boundary-aggregation

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
