# ADR-0002: Canonical Regime Classification Contract

- Status: Accepted
- Date: 2026-09-24
- Architecture: Frozen v1.0

## Context

The regime subsystem contained classification, detector, and transition skeletons but no typed boundary binding their eventual outputs to a single canonical contract. This left regime behavior structurally present but contractually unverifiable.

## Decision

Define one canonical regime classification contract at `regime/classification/regime_classifier.py`:

- `RegimeRequest` carries named numeric features, source event identity, event time, and receipt time.
- Boundary timestamps MUST be timezone-aware UTC.
- `RegimeOutput` carries a regime label, bounded confidence, source event time, regime identity, and contract version.
- Concrete classifiers implement `RegimeClassifier.classify(RegimeRequest) -> RegimeOutput`.
- The contract is synchronous and performs no provider or external I/O.
- The contract explicitly excludes look-ahead data, persistence mutation, decision finalization, and risk ownership.
- Contract identity is `regime_classification_boundary` version `1.0.0`.

The Contract Registry in `docs/contracts.md` is the only registry entry for this boundary. Contract tests and a single-source architecture test provide executable verification.

## Consequences

Future regime detectors/classifiers can be implemented independently without inventing incompatible boundary types. Temporal provenance fields are explicit at the classification boundary.

This decision does not implement the concrete regime detectors, transition components, or historical persistence behavior; those remain separate implementation work and cannot be treated as released behavior until their contracts and coverage gates pass.

## Verification

- `tests/contract/test_regime_contract.py`
- `tests/architecture/test_regime_top_level.py`
- Architecture/dependency validator
