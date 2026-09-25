# ADR 0012 — Workflow Placeholder Policy

- Status: Accepted
- Date: 2026-09-24
- Scope: GitHub Actions workflows

## Decision

A workflow is not considered a compliance control merely because the YAML file exists. Every workflow must have an explicit responsibility, a real trigger, executable verification or delivery behavior, and fail-closed handling for missing evidence.

Placeholder/no-op workflows are not permitted as substitutes for a gate.

The release workflow `.github/workflows/cd.yml` is a release-verification workflow and is not treated as G08 evidence until its release provenance is cryptographically bound as required by the Compliance Kit.

The header-normalization workflow is an operational repository-maintenance workflow; it is not itself a compliance gate and must not be used as evidence for G01-G08.

## Evidence boundary

Workflow presence is not workflow effectiveness. Gate claims require successful executable runs with the applicable evidence.

## Revisit condition

Any new workflow or material workflow change must declare its purpose and gate ownership. If a workflow becomes no-op, partially executable, or non-fail-closed, the affected gate becomes NOT VERIFIED until corrected.
