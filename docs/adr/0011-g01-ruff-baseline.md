# ADR 0011 — G01 Ruff Baseline

- Status: Accepted
- Date: 2026-09-24
- Gate: G01 Format/Lint

## Decision

Ruff is a required G01 formatter/linter and is pinned in `constraints-ci.txt`. G01 executes both `ruff check .` and `ruff format --check .`.

The baseline is zero tolerated Ruff violations: no ignore list, generated-code exemption, or warning suppression may be introduced merely to make G01 green.

Any intentional exception must be narrowly scoped, documented, and independently reviewed against the Compliance Kit precedence rules.

## Evidence boundary

Ruff version existence is distinct from dependency reproducibility. G01 owns formatter/linter correctness; G06 owns complete dependency integrity and transitive reproducibility.

## Revisit condition

A Ruff configuration change that weakens the selected rules, introduces broad exclusions, or changes the pinned tool version requires a new ADR review and a fresh G01 evidence chain.
