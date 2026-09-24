# ADR-014 — Executable Consumer Before Contract Verification

- Status: Accepted
- Date: 2026-09-24
- Scope: Contract implementation and verification lifecycle

## Decision

A contract MUST NOT be implemented solely because it exists in the frozen registry.

Before implementation, the project MUST establish:

1. a legitimate executable producer/consumer relationship;
2. the owning architecture layer and dependency direction;
3. any overlap with existing contracts, especially provenance semantics.

If no legitimate consumer exists, implementation stops. The contract remains NOT VERIFIED and the orphan is recorded in the Consumer Matrix/Gap Register. An interface-only contract requires an explicit architecture decision and MUST NOT be presented as runtime verification.

Once a legitimate consumer exists, the implementation sequence is:

1. immutable typed contract semantics;
2. known-value, invariant, boundary, and regression tests;
3. executable consumer behavior with an observable result;
4. registry binding to the actual implementation and consumer;
5. successful applicable CI gates;
6. evidence fingerprint and commit SHA freeze before VERIFIED.

## First vertical slice

The first executable vertical slice is:

MarketDataEvent -> persistence.MarketDataStore -> SQLite replay

MarketDataStore.write() persists the immutable event and read_all() reconstructs the same typed event. The event ID is the canonical deterministic identity and is the SQLite uniqueness key. Replaying the same event is idempotent.

## Consequences

- Contract count cannot grow independently of runtime behavior.
- A healthy registry with no executable consumers is explicitly treated as incomplete.
- market_data_event now has a real persistence consumer, but it remains unverified until CI evidence is captured.
- Subsequent contracts must repeat the consumer-first audit before implementation.
