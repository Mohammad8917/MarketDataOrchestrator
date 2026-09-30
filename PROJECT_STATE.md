# PROJECT_STATE.md

> AUTO-GENERATED. DO NOT EDIT.
> Generated: 2026-09-30 20:27 UTC
> Source: git log + evidence/ + docs/adr/
> WARNING: This file is a diagnostic snapshot, not the canonical source of truth.
> PENDING means no exact-SHA gate evidence is recorded in evidence/sha_status; it does not by itself mean the gate failed.
> For current truth, verify main and the exact commit SHA against GitHub Actions evidence.

---

## 1. Current State

- Branch: fix/tehran-project-state-time
- SHA: 625393279764eea603836fd7c5c27b1464b36a48
- Short: 6253932
- Last commit: fix: record project state time in Tehran timezone
- Date: 2026-09-30 23:54:45 +0330
- Phase (auto): Product development

## 2. Gate Status

- G01: SUCCESS
- G02: SUCCESS
- G03: SUCCESS
- G04: SUCCESS
- G05: SUCCESS
- G06: SUCCESS
- G07: SUCCESS

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
- 0031-regime-semantic-label-contract.md — ADR-0031: Canonical Regime Semantic Labels
- 0032-regime-rule-based-classifier-contract.md — ADR-0032: Deterministic Rule-Based Regime Classifier
- 0033-regime-feature-construction-contract.md — ADR-0033: Regime Feature Construction Contract
- 0034-regime-feature-methodology-contract.md — ADR-0034: Deterministic Regime Feature Methodology Contract
- 0035-regime-uncertainty-contract.md — ADR-0035: Regime Uncertainty Contract
- 0036-volatility-state-contract.md — ADR-0036: Volatility State Contract
- 0037-regime-analysis-consumer.md — ADR-0037: Deterministic Regime Analysis Consumer
- 0038-analysis-consumer-dependency-amendment.md — ADR-0038: Analysis Consumer Dependency Amendment
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

- d78899a4 — UNKNOWN — 2026-09-30 — chore: auto-update project state [skip ci]
- 62539327 — PASS — 2026-09-30 — fix: record project state time in Tehran timezone
- 6d1d0a53 — UNKNOWN — 2026-09-30 — chore: auto-update project state [skip ci]
- a5388234 — UNKNOWN — 2026-09-30 — chore: auto-update project state [skip ci]
- a0733135 — PASS — 2026-09-30 — feat: cover automatic state sync on every branch
- 48f0232b — UNKNOWN — 2026-09-30 — chore: auto-update project state [skip ci]
- 32dbd146 — UNKNOWN — 2026-09-30 — feat: cover automatic state sync on every branch
- 40f57d8b — UNKNOWN — 2026-09-30 — chore: auto-update project state [skip ci]
- fc79df7e — UNKNOWN — 2026-09-30 — chore: auto-update project state [skip ci]
- 93a59b3b — PASS — 2026-09-30 — chore: harden automatic project state synchronization
- 75d37e0f — UNKNOWN — 2026-09-30 — chore: harden automatic project state synchronization
- 630965fc — UNKNOWN — 2026-09-30 — chore: auto-update project state [skip ci]
- ebc7c2bf — UNKNOWN — 2026-09-30 — chore: auto-update project state [skip ci]
- ed3b6e2b — PASS — 2026-09-30 — Merge pull request #46 from Mohammad8917/feat/market-structure-contract
- 348daa73 — UNKNOWN — 2026-09-30 — test: update registry count for market structure

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
| MarketBar | shared/contracts/market_bar.py | YES |
| DonchianStrategy | strategy/trend/donchian.py | YES |
| StrategyBacktestEngine | backtest/strategy_engine.py | YES |
| PerformanceMetrics | strategy/evaluation/performance_metrics.py | YES |

## 7. Auto Notes

## Recent Commits (auto)
- chore: auto-update project state [skip ci]
- fix: record project state time in Tehran timezone
- chore: auto-update project state [skip ci]
- chore: auto-update project state [skip ci]
- feat: cover automatic state sync on every branch

## Recent ADRs (auto)
- ADR-015-sqlite-event-persistence-semantics
- ADR-011-temporal-event-boundary
- ADR-017-terminal-contract-registry-extension
- ADR-TEST-ORACLE
- ADR-014-executable-consumer-before-verification

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
