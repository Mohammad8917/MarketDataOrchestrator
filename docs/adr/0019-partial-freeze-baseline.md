# ADR 0019 — Partial Freeze Baseline

- Status: Accepted
- Date: 2026-09-24
- Gate scope: G01 / G02 / G04 / Compliance Registry / Security & Supply Chain
- Baseline SHA: `217dc1e8ea0186d0439e494118b0878ac9c9c9e0`
- Freeze type: Partial Freeze

## Context

The audit requires a reproducible baseline before the Indicator implementation sequence begins. The baseline is intentionally partial: G03 remains open because its fail-closed skeleton guards report active executable verification and production skeletons.

The freeze therefore protects the gates that are already green without claiming that the repository as a whole is release-ready.

## Baseline evidence

At baseline SHA `217dc1e8ea0186d0439e494118b0878ac9c9c9e0`:

- Compliance CI #410:
  - G01_FORMAT_LINT: PASS
  - G02_TYPECHECK: PASS
  - G04_ARCHITECTURE_DEPENDENCY: PASS
  - G03_UNIT_CONTRACT: FAIL, limited to the known skeleton guards
- Compliance Registry #337: PASS
- Security & Supply Chain #411: PASS

The baseline is therefore a protected architectural/compliance reference, not a full-green CI state.

## Decision

The following are frozen at the baseline SHA for the remainder of the current Indicator sequence:

1. G01_FORMAT_LINT behavior and its green baseline.
2. G02_TYPECHECK behavior and its green baseline.
3. G04_ARCHITECTURE_DEPENDENCY behavior and its green baseline.
4. Compliance Registry validation and reconciliation behavior.
5. Security & Supply Chain validation.
6. The G03 fail-closed skeleton finding is carried forward; it MUST NOT be weakened, bypassed, reclassified, or hidden to obtain green CI.

New implementation work may proceed on top of this baseline only when it preserves the protected gates and records a new SHA with fresh evidence.

## Break-freeze triggers

The partial freeze MUST be considered broken immediately if any of the following occurs:

- G01, G02, or G04 turns non-green on a new SHA.
- Compliance Registry turns non-green.
- Security & Supply Chain turns non-green.
- A protected validator, gate dependency, or workflow topology is changed in a way that invalidates comparison with the baseline.
- A frozen contract, its authoritative registry binding, or its governance rule is changed without an explicit new ADR/evidence decision.
- The known G03 skeleton failure is weakened, skipped, deleted, or otherwise altered solely to make the gate pass.
- A new implementation introduces a regression into the protected baseline behavior.

When a trigger occurs, the current sequence MUST stop at the failing task, the failure MUST be recorded in the Gap Register, and no task may be marked complete until a replacement baseline is established.

## Non-goals

This ADR does not declare G03 green, does not authorize release, and does not freeze future Indicator implementations. It only establishes the protected comparison baseline for the current sequence.

## Revisit condition

Replace this partial freeze with a new explicit baseline ADR when G03 is closed or when the protected gate set materially changes.
