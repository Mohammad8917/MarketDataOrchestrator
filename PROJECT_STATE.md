# PROJECT_STATE.md

> AUTO-GENERATED. DO NOT EDIT.
> Generated: 2026-09-28 13:39 UTC
> Source: git log + evidence/ + docs/adr/
> WARNING: This file is a diagnostic snapshot, not the canonical source of truth.
> PENDING means no exact-SHA gate evidence is recorded in evidence/sha_status; it does not by itself mean the gate failed.
> For current truth, verify main and the exact commit SHA against GitHub Actions evidence.

---

## 1. Current State

- Branch: main
- SHA: 1fb844d2105e387ebda09e54a3d9b54a8a9638d0
- Short: 1fb844d
- Last commit: Merge pull request #16 from Mohammad8917/fix/auto-state-successor-detection
- Date: 2026-09-28 17:07:54 +0330
- Phase (auto): Product development

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
- 0030-no-cycle-policy.md — ADR-0030 — Frozen No-Cycle Architecture Policy
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
- GAP-024 — Strategy ↔ backtest architecture policy contradiction
- GAP-025 — Layer-graph cycle detection
- GAP-026 — Cross-layer cycle regression tests
- GAP-027 — Duplicate G06 security workflow
- GAP-028 — Duplicate strict-mypy gate
- GAP-029 — G05 coverage scope limited to current executable product surface
- GAP-030 — Dependency integrity hashes
- GAP-031 — Repository-wide strict mypy enforcement
- GAP-032 — Frozen no-cycle architecture policy

## 5. Recent SHA History (auto)

- 1fb844d2 — UNKNOWN — 2026-09-28 — Merge pull request #16 from Mohammad8917/fix/auto-state-successor-detection
- c299dc0b — UNKNOWN — 2026-09-28 — fix: detect generated-state successor deterministically
- 4d617c04 — UNKNOWN — 2026-09-28 — chore: auto-update project state [skip ci]
- 8f0ad7a6 — UNKNOWN — 2026-09-28 — Merge pull request #15 from Mohammad8917/fix/auto-state-collect-after-checkout
- cf153994 — UNKNOWN — 2026-09-28 — fix: collect CI evidence after selecting state target
- 3baacffa — UNKNOWN — 2026-09-28 — chore: auto-update project state [skip ci]
- 5ff5f518 — UNKNOWN — 2026-09-28 — Merge pull request #14 from Mohammad8917/fix/auto-state-race-guard
- d055e4b0 — UNKNOWN — 2026-09-28 — fix: allow only state-only successors in Auto State
- a85275ef — UNKNOWN — 2026-09-28 — chore: auto-update project state [skip ci]
- 9f65868c — UNKNOWN — 2026-09-28 — Merge pull request #13 from Mohammad8917/fix/auto-state-evidence-sync
- f3f46327 — UNKNOWN — 2026-09-28 — style: format verified source SHA lookup
- ced60b52 — UNKNOWN — 2026-09-28 — test: cover verified source SHA state generation
- 6b10d866 — UNKNOWN — 2026-09-28 — style: use explicit os import for state source
- 6baa8710 — UNKNOWN — 2026-09-28 — fix: reconcile auto-state race with verified CI evidence
- 49b85c43 — UNKNOWN — 2026-09-28 — fix: generate state from verified CI source SHA

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

## Current executable product surface (auto)

Only files present on the checked-out SHA are listed as implemented surface.

| Capability | File | Present on this SHA |
|---|---|---|
| MarketDataEvent | domain/market_data_event.py | YES |
| MarketDataStore | persistence/market_data_store.py | YES |
| SimpleBacktestEngine | backtest/engine.py | YES |
| EquityCurveData | shared/contracts/equity_curve.py | YES |
| BinanceProvider | ingestion/providers/binance_provider.py | YES |
| MarketBar | shared/contracts/market_bar.py | NO |
| DonchianStrategy | strategy/trend/donchian.py | NO |
| StrategyBacktestEngine | backtest/strategy_engine.py | NO |
| PerformanceMetrics | strategy/evaluation/performance_metrics.py | YES |

## 7. Auto Notes

## Recent Commits (auto)
- Merge pull request #16 from Mohammad8917/fix/auto-state-successor-detection
- fix: detect generated-state successor deterministically
- chore: auto-update project state [skip ci]
- Merge pull request #15 from Mohammad8917/fix/auto-state-collect-after-checkout
- fix: collect CI evidence after selecting state target

## Recent ADRs (auto)
- ADR-015-sqlite-event-persistence-semantics
- ADR-007-regime-location
- ADR-011-temporal-event-boundary
- ADR-017-terminal-contract-registry-extension
- ADR-TEST-ORACLE

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
