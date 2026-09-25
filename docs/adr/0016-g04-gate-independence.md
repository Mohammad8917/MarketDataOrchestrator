# ADR 0016 — G04 Architecture Gate Independence

- Status: Accepted
- Date: 2026-09-24
- Gate: G04
- Scope: CI dependency between G03 unit/contract verification and G04 architecture/dependency verification

## Decision

G04 architecture/dependency verification executes independently of G03 unit/contract verification after G02 type checking succeeds.

The CI graph is therefore:

**G01 → G02 → (G03, G04)**

G04 MUST NOT use G03 as a prerequisite because the G04 validators inspect architecture/dependency constraints and do not consume the G03 contract-registry reconciliation result as an execution prerequisite.

## Rationale

1. G03 and G04 verify different control surfaces.
2. A G03 skeleton/completeness failure must not suppress independent G04 architecture/dependency evidence.
3. Independent execution makes an architecture failure attributable to G04 rather than to an upstream G03 status.
4. G03 remains fail-closed; independence of G04 does not make the overall compliance chain green when G03 is red.

## Downstream chain rule

Independence is limited to G04 execution and evidence production.

G05 MUST require both G03 and G04. Therefore a failed G03 continues to block the downstream verification chain even when G04 passes.

The effective release-verification dependency remains fail-closed:

**G01 → G02 → (G03, G04) → G05 → G06 → G07**

with G05 requiring successful completion of both G03 and G04.

## Evidence semantics

A G04 result is valid evidence only for the G04 architecture/dependency control. A successful G04 run MUST NOT be interpreted as proof that G03 is compliant, and a successful G03 run MUST NOT be interpreted as proof that G04 is compliant.

## Revisit condition

Revisit this ADR if G04 validators begin consuming G03-generated artifacts as required inputs, if gate ownership changes, or if the frozen architecture changes the dependency relationship between contract verification and architecture/dependency verification.
