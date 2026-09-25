# ADR-0029 — Public Repository Surface and License Boundary

## Status

Accepted for the current repository reconciliation.

## Decision

1. `docs/README.md` remains the authoritative Architecture & Implementation Compliance Kit.
2. Root `README.md` is the public-facing project overview and MUST describe only verified/current capabilities.
3. A root `LICENSE` file is permitted as the canonical legal notice for the proprietary repository. This explicitly amends the prior frozen-tree restriction that prohibited introducing a separate LICENSE solely from a generic template.
4. `docs/HANDOFF.md` is the single operational handoff registry. A root `HANDOFF.md` is not permitted.
5. The fifteen-exchange list is a capability target, not an implementation claim. Provider implementation status MUST be backed by executable code and current provider evidence.

## Rationale

The public repository surface must distinguish project overview, architecture authority, legal notice, and operational handoff. This removes shadow registries and prevents capability targets from being presented as implemented functionality.

## Consequences

- Public readers get a concise, evidence-based entry point.
- The full compliance Kit remains durable and machine-auditable under `docs/README.md`.
- License presence is explicit without implying an open-source license grant.
- Every future provider must be represented as implemented only after executable verification.
