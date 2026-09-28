# ADR-0030 — Frozen No-Cycle Architecture Policy

## Status

Accepted.

## Decision

The frozen v1.0 architecture has a strict no-cycle policy at both the file and layer graph levels.

1. The architecture dependency validator MUST detect cycles in the file dependency graph.
2. The architecture dependency validator MUST also detect cycles in the layer dependency graph.
3. No layer dependency is permitted solely because its corresponding file graph happens to be acyclic.
4. The current frozen policy contains no cycle exception.
5. A future architecture change that intentionally introduces a cycle requires a new architecture-amendment ADR before the dependency policy is changed. The amendment MUST update the architecture map, validator policy, and regression tests together.

The research relationship remains directional: `backtest` may consume `strategy`, while `strategy` does not depend on `backtest`.

## Rationale

File-level cycle detection alone cannot detect a layer-level cycle when different files represent each side of the dependency. Enforcing the same no-cycle invariant on both graphs makes the validator match the frozen architecture policy.

## Consequences

- Layer policy cannot silently permit a cycle that file-level analysis misses.
- The strategy/backtest dependency is directional and remains suitable for research-only evaluation.
- Any future architectural exception is explicit, reviewable, and machine-guarded.
