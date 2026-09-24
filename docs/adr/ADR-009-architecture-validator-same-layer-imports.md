# ADR-009: Same-Layer Imports in Architecture Validation

**Status:** Accepted for frozen v1.0 validation semantics

## Decision

An import whose source and target belong to the same architecture layer is an internal implementation dependency and is not a cross-layer architecture edge.

The architecture validator MUST:
- permit same-layer imports;
- exclude same-layer imports from the layer-level dependency graph;
- continue rejecting imports from a layer to a disallowed different layer;
- continue detecting cycles among cross-layer dependency edges.

This does not weaken ownership rules. File headers remain authoritative for file-level responsibility and dependencies.

## Regression requirement

The validator test suite MUST contain:
- a same-layer import accepted case;
- a forbidden cross-layer import rejected case;
- a cycle case where applicable.

