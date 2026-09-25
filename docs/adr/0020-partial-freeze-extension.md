# ADR 0020 — Partial Freeze Extension After Indicator and Registry Milestone

- Status: Accepted
- Date: 2026-09-24
- Gate scope: G01 / G02 / G04 / Compliance Registry / Security & Supply Chain
- Original baseline SHA: `217dc1e8ea0186d0439e494118b0878ac9c9c9e0`
- Extension SHA: `96ab3255e92d484fd088bcff39089ef47d4148e5`
- Freeze type: Partial Freeze — Extended

## Decision

The partial freeze established by ADR 0019 is extended after completion of the six-indicator milestone, the canonical indicator registry, the Bollinger-to-SMA integration test, and the IndicatorOutput consumer audit.

Protected gates remain unchanged:

- G01_FORMAT_LINT
- G02_TYPECHECK
- G04_ARCHITECTURE_DEPENDENCY
- Compliance Registry
- Security & Supply Chain

The G03 skeleton guard remains fail-closed and unchanged. The extension does not claim G03 closure or release readiness.

## Extension evidence

At the extension SHA:

- Compliance CI #452: G01 PASS, G02 PASS, G04 PASS; G03 fails only on the pre-existing active skeleton guards.
- Compliance Registry #379: PASS.
- Security & Supply Chain #453: PASS.
- Consumer-matrix validator: PASS.
- Bollinger-to-SMA integration evidence: PASS.
- Indicator registry evidence: PASS.
- IndicatorOutput remains an explicit ACTIVE-ORPHAN; no fake consumer was introduced.

## Break-freeze triggers

The triggers in ADR 0019 remain in force. In addition, the extension is broken if any of the six implemented indicators or the registry changes without a fresh protected-gate run and evidence update.

