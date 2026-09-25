# ADR 0015 — Evidence Artifact Lifecycle

- Status: Accepted
- Date: 2026-09-24
- Gate: G03
- Scope: Source-controlled machine-generated G03 evidence artifacts

## Decision

Machine-generated compliance evidence is derived data, not an independent source of truth.

For the G03 contract-registry reconciliation artifact:

1. `validation/contract_registry_validator.py` is the authoritative generator.
2. `evidence/G03_CONTRACT_REGISTRY_RECONCILIATION.json` is the committed evidence snapshot.
3. The snapshot MUST be regenerated from the current source-controlled registry, frozen inventory, and ADR inputs before acceptance.
4. CI MUST compare the regenerated artifact with the committed artifact and fail on any difference.
5. Manual edits to the generated artifact are not a valid drift correction; the generator or its authoritative inputs must be corrected instead.
6. Any source/input change invalidates prior evidence for the affected artifact and requires a fresh G03 run on the new SHA.
7. A clean comparison proves artifact synchronization only; it does not by itself prove that the underlying contract control is semantically compliant.

## Lifecycle

**authoritative inputs → deterministic generator → committed evidence snapshot → CI regenerate + compare → gate evidence**

A mismatch is an **Evidence Drift** finding and is release/gate blocking until the authoritative input/generator is reconciled and a fresh artifact is committed.

## Revisit condition

If the evidence generator, authoritative input set, artifact schema, or CI verification mechanism changes materially, this ADR and the affected G03 control must be reviewed and fresh evidence established.
