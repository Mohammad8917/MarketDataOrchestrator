# PROJECT_STATE.md

> AUTO-GENERATED. DO NOT EDIT.
> Generated: 2026-09-30 13:48 UTC
> Source: git log + evidence/ + docs/adr/
> WARNING: This file is a diagnostic snapshot, not the canonical source of truth.
> PENDING means no exact-SHA gate evidence is recorded in evidence/sha_status; it does not by itself mean the gate failed.
> For current truth, verify main and the exact commit SHA against GitHub Actions evidence.

---

## 1. Current State

- Branch: main
- SHA: 5844c88d76e3fc83cccd8c5097e4947d31ced7bf
- Short: 5844c88
- Last commit: Merge pull request #44 from Mohammad8917/feat/regime-analysis-consumer
- Date: 2026-09-30 17:14:56 +0330
- Phase (auto): Reconciliation

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

- 5d900b81 — UNKNOWN — 2026-09-30 — chore: auto-update project state [skip ci]
- 5844c88d — PASS — 2026-09-30 — Merge pull request #44 from Mohammad8917/feat/regime-analysis-consumer
- 6e37388f — UNKNOWN — 2026-09-30 — fix: update contract registry count assertion
- 47e11e8f — UNKNOWN — 2026-09-30 — fix: repair consumer matrix JSON
- 7a5bc601 — UNKNOWN — 2026-09-30 — fix: align G03 reconciliation artifact ordering
- 52d3039e — UNKNOWN — 2026-09-30 — fix: restore complete G03 reconciliation artifact
- 64c1301d — UNKNOWN — 2026-09-30 — fix: reconcile G03 evidence ordering with canonical inventory
- 98d9a904 — UNKNOWN — 2026-09-30 — fix: apply ruff formatting to regime analysis
- 6fb190dd — UNKNOWN — 2026-09-30 — docs: add regime analysis G03 reconciliation reason
- 0d6720af — UNKNOWN — 2026-09-30 — style: format regime analysis contract tests
- b13f68fb — UNKNOWN — 2026-09-30 — fix: restore acyclic architecture and formatting
- fef96a04 — UNKNOWN — 2026-09-30 — docs: record analysis dependency architecture amendment
- 9cef2acc — UNKNOWN — 2026-09-30 — arch: allow analysis consumers of regime and volatility
- 3bd715bd — UNKNOWN — 2026-09-30 — fix: restore regime analysis contract to analysis layer
- 00bb153d — UNKNOWN — 2026-09-30 — fix: restore regime analysis contract to analysis layer

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
- Merge pull request #44 from Mohammad8917/feat/regime-analysis-consumer
- fix: update contract registry count assertion
- fix: repair consumer matrix JSON
- fix: align G03 reconciliation artifact ordering

## Recent ADRs (auto)
- ADR-TEST-ORACLE
- ADR-004-forex-gold-status
- ADR-015-sqlite-event-persistence-semantics
- ADR-007-regime-location
- ADR-011-temporal-event-boundary

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
