# ADR-010: Deterministic Canonical Market Event Identity

**Status:** Accepted

## Decision

Canonical `MarketDataEvent.event_id` is content-derived and deterministic. UUID4 generation is not permitted as the canonical identity mechanism.

The identity is derived from a canonical serialization of the event's stable semantic fields and UUID5 under a fixed namespace. The derivation MUST be stable across replay, process, and machine boundaries.

Provider-specific source identity and raw-payload digest are provenance concerns and MUST NOT be silently conflated with the canonical domain event identity.

## Consequences

- Replay of identical canonical event content produces the same event identity.
- Evidence and regression fingerprints may safely refer to the canonical event identity.
- A future ingestion/provider contract may preserve `source_event_id` and `payload_digest` as provenance fields.
- Any change to the canonical identity serialization is a contract/versioning change and requires explicit review.

