# ADR-011: Temporal Event Boundary

**Status:** Proposed — blocking decision

## Finding

The Contract Registry currently names `temporal_event_boundary` with owner layer `temporal`, but `temporal` is not a layer in the frozen Architecture Map.

## Interim decision

No implementation may bind `temporal_event_boundary` until its ownership is formally resolved.

No implicit `temporal` layer is added by implementation.

## Required decision

The architecture owner MUST decide whether temporal semantics are:
1. a domain contract owned by `domain`; or
2. a dedicated architecture layer requiring a frozen Architecture Map amendment.

Until that decision is recorded, the contract remains NOT VERIFIED.

