# Compliance Gap Register

This file is the current audit trail for known gaps in the repository. Historical branch/SHA references are retained as evidence and are not claims about the current `main` state.

Status rules:
- **OPEN** = unresolved and retained for active work.
- **RESOLVED (date)** = closed by the documented fix; retained for audit trail.
- Historical CI evidence does not constitute a PASS for a newer SHA.

## Documentation lineage — duplicate root handoff

**Finding:** The audit branch contained both `HANDOFF.md` at repository root and the canonical `docs/HANDOFF.md`, with conflicting state claims.

**Status:** RESOLVED (2026-09-26)

**Fix:** Removed the root-level duplicate. `docs/HANDOFF.md` is now the sole canonical handoff and explicitly states that protected CI evidence for the exact SHA is authoritative.

**Evidence:** Commit removing root `HANDOFF.md`; canonical handoff updated in the same reconciliation sequence.

## G03 — Contract registry ↔ frozen inventory reconciliation

**Finding:** Executable reconciliation was initially absent. The registry now has machine-checked bindings for the frozen contract models and a committed reconciliation artifact.

**Status:** RESOLVED (2026-09-25)

**Fix:** Corrected the reconciliation artifact and retained executable validator/regression-test enforcement.

**Evidence:** `evidence/G03_CONTRACT_REGISTRY_RECONCILIATION.json`; ADR 0015 — `docs/adr/0015-evidence-artifact-lifecycle.md`.

**Threat-model boundary:** G03 does not cover hostile in-process mutation, deserialization tampering, or hostile plugin/provider code; those excluded threats remain assigned to G06 by ADR 0009.

## G03 — Runtime consumer definition and MarketEvent registry reconciliation

**Finding:** The strict runtime-reader definition established `ingestion.IngestionService` as a current `MarketEvent` consumer, while the registry previously omitted `ingestion`.

**Status:** RESOLVED (2026-09-25)

**Fix:** Reconciled `market_data_event.allowed_consumers` to include `ingestion` and formalized the runtime-reader definition in ADR 0017.

**Evidence:** `docs/adr/0017-runtime-consumer-definition.md`; `docs/contracts.md`; `evidence/G03_CONSUMER_MATRIX.json`.

## G03 — Compliance registry contract-count reporting

**Finding:** The validator counted the Markdown `contract_id` header as a contract row.

**Status:** RESOLVED (2026-09-25)

**Fix:** Excluded the header row and locked the expected data-row count with an executable regression test.

**Evidence:** `validation/compliance_registry_validator.py`; `tests/architecture/test_compliance_registry_validator.py`.

## G03 — Consumer audit baseline

**Finding:** The runtime consumer matrix distinguishes active runtime consumers, active orphans, and future consumers. It is an audit baseline, not an implementation-completeness waiver.

**Status:** OPEN — ongoing enforcement

**Action:** Keep the matrix synchronized with executable consumer evidence. Every future runtime reader must reconcile its contract registry declaration.

**Evidence:** `evidence/G03_CONSUMER_MATRIX.json`; `docs/adr/0017-runtime-consumer-definition.md`.

**Evidence integrity:** The audited baseline fingerprint was `7dbe2f9fb89700bd51a166d4df6443676ec219e7a543fa6528c6b50bbc46746d`; it must change whenever the matrix changes.

## G03 — Executable verification skeleton inventory

**Finding:** The historical audit recorded 428 active skeleton entries before package-boundary cleanup (398 production, 30 test), with a historical active backlog of 355 after 73 package initializers were excluded.

**Status:** OPEN — implementation program remains active

**Action:** Do not weaken skeleton guards. Scope is controlled by `docs/compliance/IMPLEMENTATION_PHASE_MANIFEST.json`, ADR 0013, and ADR 0014. Active skeletons must be implemented or formally reclassified; each implementation requires explicit export/consumer binding.

**Evidence boundary:** The 428/355 figures are historical audit evidence, not a current-count claim for the latest SHA. Fresh protected evidence is required before declaring the inventory complete.

**Gate rule:** G03 remains fail-closed for manifest-declared scope. Unknown/unclassified skeletons remain visible findings.

**Current references:** ADR 0013 — `docs/adr/0013-phase-plan-implementation-completeness.md`; ADR 0014 — `docs/adr/0014-module-export-consumer-binding.md`.

## G03 — Architecture scope / consumer viability

**Finding:** The historical skeleton baseline contained capability groups whose executable downstream consumers did not yet exist; the prior audit identified 134 future-consumer-only production entries across analysis, strategy, and composition.

**Status:** OPEN — architecture/scope review required

**Action:** Bind each affected module to a justified executable consumer/phase, or formally remove/reclassify it. Do not implement speculative consumers.

**Evidence boundary:** The 134-entry figure is historical evidence, not a current-count claim for the latest SHA.

**Evidence:** ADR 0014 — `docs/adr/0014-module-export-consumer-binding.md`; frozen layer/dependency rules.

## G06 — Transitive dependency reproducibility

**Finding:** Direct CI tooling versions are pinned and verified, but complete transitive dependency integrity/reproducibility is not established.

**Status:** OPEN — NOT VERIFIED

**Action:** Establish a committed resolved transitive lock artifact, integrity/hash material, CI installation/verification from that artifact, deterministic repeat-resolution evidence, and provenance binding to the source commit.

**Evidence:** ADR 0010 — `docs/adr/0010-g06-transitive-dependency-reproducibility.md`.

**Closure rule:** No G06 PASS is claimed until all closure controls execute successfully for the same source commit.

## SMA — Active-orphan implementation

**Finding:** `indicators/trend/sma.py` is implemented and bound to the canonical `indicator_execution_boundary`, but its executable downstream analysis/strategy consumer is not yet present.

**Status:** OPEN — active-orphan

**Consumer:** Future analysis/strategy consumer through the canonical Indicator protocol.

**Action:** Revisit when the strategy/analysis phase has an executable consumer. If the real consumer requires a different interface, perform contract evolution and fresh protected evidence rather than silently changing the boundary.

## G04 — Indicator internal dependency rule regression guard

**Finding:** The validator previously rejected the legitimate same-layer `indicators -> indicators` dependency needed by concrete indicators.

**Status:** RESOLVED (2026-09-25)

**Fix:** Corrected the executable dependency rule and added regression coverage for an allowed same-layer edge and a forbidden `indicators -> strategy` edge.

**Evidence:** `validation/architecture_dependency_validator.py`; `tests/architecture/test_indicator_layer_dependency_policy.py`.

## Block 1 / Work 2 — Partial Freeze evidence triggers Security Secret Scan

**Finding:** The partial-freeze evidence artifact triggered the Security & Supply Chain secret scan.

**Status:** RESOLVED (2026-09-25)

**Fix:** Encoded the baseline SHA as non-secret-like octets; Security & Supply Chain #431 passed on the resulting SHA.

**Evidence:** Security & Supply Chain #418, job `107787064902`; resulting Security & Supply Chain #431.

**Audit note:** The historical failure remains recorded here; it is not a current green-freeze claim.

## Block 1 / Work 5 — Consumer matrix validator header compliance

**Finding:** The first consumer-matrix validator failed G04 because repository-wide architecture header validation requires the canonical file header/schema.

**Status:** RESOLVED (2026-09-25)

**Fix:** Added the canonical validation-file header and reran the applicable architecture validation.

**Evidence:** Compliance Registry #351+, job `107787934423`.

## Block 1 / Work 5 — Consumer matrix validator import/docstring ordering

**Finding:** A second module docstring preceded `from __future__ import annotations`, causing G01 Ruff failures.

**Status:** RESOLVED (2026-09-25)

**Fix:** Restored a single canonical module docstring before the future import.

**Evidence:** Compliance CI #426+, job `107788272564`, `ruff check .`.

## Block 1 / Work 5 — Consumer matrix validator formatting

**Finding:** G01 `ruff format --check` failed on the new validator and regression test.

**Status:** RESOLVED (2026-09-25)

**Fix:** Applied exact Ruff formatting without weakening the configuration.

**Evidence:** Compliance CI #440+, job `107788544922`, `ruff format --check .`.

## Block 2 / Indicator batch 1 — CI evidence

**Finding:** The initial indicator batch had a formatting-only G01 failure; subsequent evidence recorded G01/G02/G04 success while G03 remained blocked by the pre-existing skeleton guards.

**Status:** RESOLVED (2026-09-25)

**Fix:** Applied the required formatting and recorded the batch evidence. No indicator test failure was reported in the cited CI evidence.

**Evidence:** Compliance CI #440 and #442; `evidence/INDICATOR_BATCH_EMA_RSI_ATR_MACD.json`.

## GAP-014 — Bollinger mocked-band expected-value provenance

**Finding:** An integration test used hard-coded Bollinger expectations without a documented derivation.

**Status:** RESOLVED (2026-09-25)

**Fix:** Replaced the expected values with an independently calculated population-standard-deviation oracle and documented the derivation inline in `tests/integration/test_indicator_sma_bb.py`. No implementation change or tolerance relaxation was made.

**Contract:** `evidence/INDICATOR_BATCH_DONCHIAN_BOLLINGER.json` specifies population standard deviation (ddof=0), matching the implementation's division by period.

**Evidence:** `7d193c95af589c8c449a592cca30a851c490c91b`; `b62ee415b973ae5c9871e8a92e42a8c0f1bf6e09`; `b928b1890767c1e0a6547d280f32facbb7f796d6`; `6b3c28f637dbd9debc20f64b3c66608af4cf46ba`; `evidence/INDICATOR_BATCH_DONCHIAN_BOLLINGER.json`.

## GAP-022 — Main/audit architecture validator fix divergence

**Finding:** Historical main and audit lineages temporarily contained different versions of the architecture validator fix.

**Status:** RESOLVED (2026-09-28)

**Fix:** The reconciliation work was merged into `main`; the audit branch is historical rather than canonical. Current architecture behavior is governed by the implementation and tests on `main`.

**Evidence:** PR #5 reconciliation/merge history; PR #8 architecture guardrail merge `2086df2674763aacd320e4df9298a2355ec7ebbe`; current `main` validator and G04 evidence.

## GAP-008 — MarketDataStore orphan

**Finding:** `MarketDataStore` was registered as an allowed persistence consumer of `MarketDataEvent`, but no executable production runtime consumer existed for `read_all()`.

**Resolution:** The first executable backtest vertical slice now provides:
```
MarketDataStore.read_all()
    ↓
SimpleBacktestEngine.run()
    ↓
EquityCurveData
    ↓
backtest result output
```

**Verification:** The end-to-end integration test persists fake `MarketDataEvent` instances, replays them through `MarketDataStore.read_all()`, executes the backtest engine, and asserts the resulting equity curve.

**Status:** RESOLVED (2026-09-25)

**Fix:** Added the executable production backtest consumer path and end-to-end integration verification.

**Evidence:** SHA `a19078c02395f6ead9ea63793d5e3f10fa53bd04`; `scripts/run_backtest.py`; `tests/integration/test_backtest_flow.py`; Compliance CI #590 for the documented protected milestone.

## GAP-024 — Strategy ↔ backtest architecture policy contradiction

**Finding:** The historical architecture policy permitted a `strategy -> backtest` dependency even though the dependency direction is intended to keep strategy independent of execution infrastructure.

**Status:** RESOLVED (2026-09-28)

**Fix:** Removed `backtest` from the strategy allowed-dependency set and locked the rule with architecture regression coverage.

**Evidence:** PR #8 merge `2086df2674763aacd320e4df9298a2355ec7ebbe`; `validation/architecture_dependency_validator.py`; `docs/adr/0030-no-cycle-policy.md`.

## GAP-025 — Layer-graph cycle detection

**Finding:** The historical architecture validator checked file-level dependency cycles but did not independently validate the derived layer graph.

**Status:** RESOLVED (2026-09-28)

**Fix:** The validator now applies the same deterministic cycle detector to both the file graph and the layer graph.

**Evidence:** PR #8 merge `2086df2674763aacd320e4df9298a2355ec7ebbe`; `validation/architecture_dependency_validator.py`.

## GAP-026 — Cross-layer cycle regression tests

**Finding:** The historical validator test suite did not explicitly lock cross-layer cycle detection with regression cases.

**Status:** RESOLVED (2026-09-28)

**Fix:** Added file-level and layer-level cycle regression tests and consolidated the architecture validator test coverage.

**Evidence:** PR #8 merge `2086df2674763aacd320e4df9298a2355ec7ebbe`; `tests/validation/test_architecture_dependency_validator.py`.

## GAP-027 — Duplicate G06 security workflow

**Finding:** G06 security verification was historically duplicated across the canonical Compliance CI and a separate `security-scan.yml` workflow, creating duplicate execution paths and ambiguity about the authoritative gate.

**Status:** RESOLVED (2026-09-28)

**Fix:** Removed the duplicate workflow and retained G06 only in the ordered Compliance CI.

**Evidence:** PR #9 merge `7d7db99b0525280ef8bf3bb9b8c06f0407c1b651`; `.github/workflows/ci.yml`.

## GAP-028 — Duplicate strict-mypy gate

**Finding:** Strict mypy verification was historically duplicated in CI outside the canonical ordered gate sequence.

**Status:** RESOLVED (2026-09-28)

**Fix:** Removed the duplicate strict-mypy gate and kept the canonical G02 typecheck sequence in Compliance CI.

**Evidence:** PR #9 merge `7d7db99b0525280ef8bf3bb9b8c06f0407c1b651`; `.github/workflows/ci.yml`.

## GAP-029 — G05 coverage scope limited to current executable product surface

**Finding:** G05 historically enforced 100% branch coverage only for a small, explicitly enumerated set of executable product files. This is a scoped 100% claim, not repository-wide coverage.

**Status:** OPEN — scope expansion in progress

**Effect:** A visitor must not interpret a green G05 result as proof that every Python file in the repository has 100% branch coverage.

**Current scope on `main`:** five files, defined by `docs/coverage-policy.md` and `coverage.ini`.

**Expansion path:** Product vertical slices add their executable files to the same 100% scope. PR #11 is the next expansion and, while not yet merged to `main`, covers nine files.

**Evidence:** `docs/coverage-policy.md`; `coverage.ini`; PR #10 merge `7d0cb60a6ec12c571903f6ba4ef7e81cafb86c1e`; PR #11 is not part of `main` until merged.

## GAP-030 — Dependency integrity hashes

**Finding:** CI constraint files pin exact package versions, but installation is not yet enforced with cryptographic hashes from a committed resolved transitive lock artifact.

**Status:** OPEN — NOT VERIFIED

**Effect:** Version pinning alone does not provide complete artifact-integrity or repeat-resolution guarantees.

**Action:** Introduce a committed resolved transitive lock artifact with hashes, require hash-verified installation in CI, and bind the resulting evidence to the exact source SHA.

**Evidence:** `constraints-ci.txt`; `constraints-security.txt`; ADR 0010 — `docs/adr/0010-g06-transitive-dependency-reproducibility.md`.

## GAP-031 — Repository-wide strict mypy enforcement

**Finding:** G02 currently runs `mypy .` and an additional `mypy --strict` check for `tests/property` and `tests/benchmark`, but the entire repository is not yet enforced under `mypy --strict`.

**Status:** OPEN — scope expansion required

**Effect:** A passing G02 result does not currently prove repository-wide strict typing.

**Action:** Expand strict typing in dependency order, resolve the existing strict findings without weakening assertions or configuration, and make the full-repository strict check part of the canonical G02 gate when the scope is ready.

**Evidence:** `.github/workflows/ci.yml`; current G02 configuration uses `mypy .` plus the explicitly scoped strict check.

## GAP-032 — Frozen no-cycle architecture policy

**Finding:** The historical architecture review identified that cycle prevention needed an explicit binding architectural decision rather than relying only on implementation behavior.

**Status:** RESOLVED (2026-09-28)

**Fix:** Added the frozen no-cycle policy and tied future exceptions to an architecture amendment ADR.

**Evidence:** PR #8 merge `2086df2674763aacd320e4df9298a2355ec7ebbe`; `docs/adr/0030-no-cycle-policy.md`.
## Removed stale/duplicate material

- Removed the obsolete reference to non-existent **ADR-0025**. Current references use the existing ADR 0013/0014 files.
- Removed the duplicate standalone **G06 reproducibility closure criteria** entry; its closure requirements are consolidated under the single G06 transitive-dependency gap.
- Removed the superseded **Block 2 / Indicator batch 1 formatting OPEN** entry because the later CI evidence already records its resolution.
