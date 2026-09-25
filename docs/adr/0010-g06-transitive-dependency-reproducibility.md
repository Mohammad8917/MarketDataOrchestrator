# ADR 0010 — G06 Transitive Dependency Reproducibility

- Status: Accepted
- Date: 2026-09-24
- Gate: G06 Security & Supply Chain

## Decision

G01 establishes exact direct-tool versions through pinned constraints and verifies that CI executes those versions. This does not establish complete transitive dependency reproducibility.

Complete transitive reproducibility is a G06 responsibility. G06 must verify the resolved dependency graph, integrity material (including hashes where supported), and the reproducibility of the resolution used for security and release verification.

A repository must not claim full dependency reproducibility merely because direct tools are version-pinned.

## Evidence boundary

Current G01 evidence proves pinned Ruff, mypy, pytest, pytest-asyncio, and coverage versions are installed by CI. Full transitive hash/integrity closure remains a G06 control.

## Revisit condition

If dependency resolution becomes environment-dependent, an unpinned transitive dependency is introduced, or release tooling consumes a different resolution from CI, G06 must reopen this ADR and fail the applicable gate until reproducibility is restored.

## Required closure evidence

G06 remains OPEN until all of the following are machine-verifiable for the same source commit:

1. Every runtime and verification dependency set used by CI/release has a resolved transitive dependency graph.
2. The resolved graph is represented by a committed, reviewable lock artifact; direct-version constraint files alone do not satisfy this control.
3. Integrity material is recorded for resolved artifacts, including hashes where the selected package tooling supports them.
4. CI installs/verifies from that resolved artifact rather than resolving a fresh unconstrained graph.
5. A reproducibility check resolves/install-checks the same artifact twice and verifies the resulting package/version/hash set is identical.
6. Release provenance records the exact lock artifact fingerprint and source commit.

Until those controls execute successfully, G06 evidence is **NOT VERIFIED** and no release-readiness claim may treat transitive reproducibility as closed.
