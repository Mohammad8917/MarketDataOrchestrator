# MarketDataOrchestrator

![Compliance CI](https://github.com/Mohammad8917/MarketDataOrchestrator/actions/workflows/ci.yml/badge.svg?branch=main)

**Architecture-first trading-system foundation — product first, compliance as a guardrail.**

<!-- LIVE-STATUS:START -->
## Live project status

- Canonical branch: main
- Exact SHA: 405ad4e7552a1c3748c479e4ee0d57f6458a9ad0
- Last commit: Merge pull request #170 from Mohammad8917/fix/harden-market-structure-replay-runtime-boundary
- Gates: G01=PENDING · G02=PENDING · G03=PENDING · G04=PENDING · G05=PENDING · G06=PENDING · G07=PENDING
- Executable product capabilities detected: 9
- Source of truth: GitHub main + exact-SHA Actions evidence
<!-- LIVE-STATUS:END -->


> ⚠️ **وضعیت پروژه: در حال توسعه فعال (In Development)**  
> این پروژه هنوز کامل نشده است. در حال حاضر فقط **۱ صرافی از ۱۵ صرافی** هدف پیاده‌سازی شده.  
> سبز بودن دروازه‌های G01–G07 به معنای **کیفیت کد** است، نه **تکمیل محصول**.  
> [مشاهده نقشه راه کامل](./ROADMAP.md)

MarketDataOrchestrator is being built as a production-oriented market-data and backtesting system. The project is developed bottom-up: boundaries and consumers are established before implementations are expanded.

> **New here? Start with this README. Do not start from a feature branch, an audit branch, or `PROJECT_STATE.md`.**

---

## 1. The canonical project

| Item | Canonical rule |
|---|---|
| **Canonical branch** | `main` |
| **Canonical entry point** | This README |
| **Canonical handoff** | [`docs/HANDOFF.md`](docs/HANDOFF.md) |
| **Architecture decisions** | [`docs/adr/`](docs/adr/) |
| **Compliance specification** | [`docs/README.md`](docs/README.md) |
| **Machine-generated state** | [`PROJECT_STATE.md`](PROJECT_STATE.md) — snapshot only, not the source of truth |

**Only work actually present on `main` is part of the current project state.**

A branch, commit, PR, or audit result is **not** part of `main` merely because it exists in the repository. Merge status must be verified on GitHub.

---

## 2. What we are building

The target execution direction is:

```
MarketDataEvent
      ↓
MarketDataStore
      ↓
BacktestEngine
      ↓
Strategy
      ↓
Evaluation
```

The current repository is intentionally being advanced as executable vertical slices rather than by filling the entire architecture horizontally.

### Current executable foundation

```
MarketDataEvent
      ↓
MarketDataStore
      ↓
SimpleBacktestEngine
      ↓
EquityCurveData
      ↓
scripts/run_backtest.py
```

The repository currently contains an executable market-data/backtest foundation, while the broader trading-system architecture is still under construction.

Implemented and exercised:

- immutable `MarketDataEvent`
- SQLite-backed `MarketDataStore`
- typed `BacktestEngine` boundary
- minimal buy-and-hold backtest execution
- immutable `EquityCurveData`
- end-to-end persistence → replay → backtest integration

---

## 3. Current provider reality

The project has a larger provider target, but targets are **not** implementation claims.

**Current executable exchange implementations: 1 / 15 (Binance).**

Binance is implemented behind the existing provider boundary. Its live public-endpoint smoke remains separate from G01–G07 and is subject to external runner/network policy.

Provider expansion follows the same rule as the rest of the system: establish the boundary, executable consumer, contract, implementation, tests, and exact-SHA verification before treating a provider as complete.

**Product progression:** new vertical slices are selected in dependency order and become part of the current project only after their implementation, tests, and exact-SHA G01–G07 evidence are merged into `main`.

---

## 4. Development model

Development is deliberately **bottom-up and dependency-aware**:

1. Define the executable consumer.
2. Establish the interface boundary.
3. Establish the contract.
4. Implement the smallest valid dependency.
5. Add tests and integration coverage.
6. Verify the exact commit.
7. Expand the next vertical slice.

The goal is to avoid circular development where upper layers are built on unfinished or ambiguous lower-layer dependencies.

---

## 5. Verification model

Compliance is a **guardrail**, not the product goal.

The locked verification sequence is:

- **G01** — format / lint
- **G02** — type checking
- **G03** — unit / contract verification
- **G04** — architecture / dependency verification
- **G05** — coverage
- **G06** — security / supply-chain verification
- **G07** — integration / resilience verification
- **G08** — release verification when a release is produced

These definitions, thresholds, ordering, and failure semantics are locked.

**No gate is weakened, reordered, or rewritten merely to obtain a green result.**

Every new SHA starts verification again from G01. Missing or stale evidence is **NOT VERIFIED**.

---

## 6. Known limitations and open findings

The repository is intentionally transparent about known limitations. A green G01–G07 result means the defined gates passed for that exact SHA; it does **not** mean every architectural or reproducibility concern is closed.

Current limitations on `main`:

- **G05 coverage is scoped, not repository-wide.** The exact covered files are maintained in the coverage policy and must be read together with the exact-SHA G05 evidence. A green G05 result must not be interpreted as 100% coverage of every Python file.
- **Dependency integrity hashes are not yet committed.** `constraints-ci.txt` and `constraints-security.txt` pin versions, but the repository does not yet enforce hash-verified installation from a resolved transitive lock artifact. See the open G06 reproducibility finding in the [Gap Register](docs/GAP_REGISTER.md).
- **Repository-wide strict typing is not yet enforced.** G02 runs normal `mypy .` plus a strict check for the property/benchmark test scope; the whole repository is not yet under `mypy --strict`. See the corresponding open finding in the [Gap Register](docs/GAP_REGISTER.md).

Previously identified architecture/CI findings are also retained in the [Gap Register](docs/GAP_REGISTER.md) with their current status, rather than being silently omitted after remediation.

---
## 7. How to read the repository without getting lost

### If you only want to understand the project

Read in this order:

1. **README** — project purpose and canonical state
2. [**HANDOFF**](docs/HANDOFF.md) — current engineering handoff
3. [**Architecture ADRs**](docs/adr/) — binding architectural decisions
4. [**Compliance Kit**](docs/README.md) — verification rules
5. [**Gap Register**](docs/GAP_REGISTER.md) — known open findings

### If you want to run the executable slice

Start with:

```text
scripts/run_backtest.py
```

Then follow the dependency chain:

```text
MarketDataEvent
→ MarketDataStore
→ SimpleBacktestEngine
→ EquityCurveData
```

### If you want to inspect machine-generated state

[**PROJECT_STATE.md**](PROJECT_STATE.md) is generated automatically from repository state and evidence.

It is useful as an automatically generated diagnostic snapshot. It can lag briefly while automation is processing a new commit or workflow result.

For current truth, resolve `main`, record its exact SHA, and use the G01–G07 Actions evidence for that SHA. Unmerged branches/PRs are proposals, not current functionality.

The auto-generated visitor status page is informational only; it never substitutes for exact-SHA GitHub Actions evidence.

---

## 8. Branches: what visitors should and should not use

### Use

**`main`** — canonical project state.

### Do not treat as canonical

**`audit/fix-known-compliance-gaps`** — historical audit branch. Its work was reconciled and merged into `main`; it is not a current canonical development line. The branch should not be used as a source of current state.

Product feature branches and open PR branches are development candidates only. Their contents are not part of `main` until an actual merge occurs.

> **Rule:** seeing a branch on GitHub does not mean its work is released or canonical. Merge status must be verified against `main`.

---

## 9. Documentation map

- [Handoff](docs/HANDOFF.md)
- [Compliance Kit](docs/README.md)
- [Gap Register](docs/GAP_REGISTER.md)
- [Coverage Policy](docs/coverage-policy.md)
- [Runbooks](docs/runbooks.md)
- [Architecture ADRs](docs/adr/)
- [Machine-generated project snapshot](PROJECT_STATE.md)
- [Current visitor status — auto-generated](docs/STATUS.md)
- [Project Info — generated](PROJECT_INFO.md)
- [Roadmap — generated provider/product view](ROADMAP.md)
- [Architecture Overview](docs/architecture/overview.md)
- [Contributing](CONTRIBUTING.md)

---

## 10. Important project rules

- `main` is canonical.
- Product-first; compliance is a guardrail.
- G01–G07 are locked.
- Every new SHA restarts verification.
- Claims require machine-verifiable evidence tied to the exact SHA.
- Fail-closed: a failed gate remains failed until its underlying cause is corrected.
- Consumer before contract.
- Interface-first.
- Vertical slice before horizontal expansion.
- Never represent branch-only work as merged or released.

---

## License

Proprietary — All Rights Reserved. See [`LICENSE`](LICENSE).
