# ADR-015: SQLite Event Identity, Replay Conflict, and Exact Numeric Persistence

**Status:** Accepted

## Context

The first executable persistence slice stores the canonical `MarketDataEvent` in SQLite. Its
identity is deterministic UUID5, while `received_at` is intentionally excluded from the
canonical identity because it describes ingestion timing rather than event semantics.

The persistence boundary therefore needs an explicit rule for duplicate identities and for
lossless storage of Decimal and timezone-aware datetime values.

## Decision

1. **Identity key:** `event_id` is the SQLite `PRIMARY KEY`.
2. **Duplicate-write behavior:** writes use `INSERT OR IGNORE`.
   - Replaying the same canonical event is idempotent.
   - A second row with the same `event_id` is not inserted and does not overwrite the
     previously stored row.
3. **`received_at` conflict:** because `received_at` is not part of identity, two otherwise
   identical events with different `received_at` values have the same `event_id`.
   The **first persisted representation wins**; later representations with that identity are
   ignored. This is intentional and prevents ingestion timing from mutating canonical replay
   state.
4. **Decimal preservation:** OHLCV values are stored as SQLite `TEXT`, using the exact
   `Decimal` string representation, and reconstructed with `Decimal`. SQLite `REAL` is
   forbidden for these canonical numeric values because binary floating-point conversion can
   lose decimal precision.
5. **Datetime preservation:** `event_time` and `received_at` are stored as ISO-8601
   `TEXT` values including their UTC offset. Reads require timezone-aware values and normalize
   them to UTC. Naive persisted datetimes are rejected.
6. **Ordering:** replay is deterministic: rows are ordered by `event_time ASC, event_id ASC`.

## Consequences

- Duplicate canonical events are silently ignored rather than overwritten or raised as errors.
- The first observed `received_at` is retained for a canonical event identity.
- Exact Decimal values survive a write/read round trip.
- Timezone information is explicit at the persistence boundary.
- Changing any of these semantics requires an ADR and corresponding contract/regression tests.

## Verification

The persistence contract tests MUST verify:
- write/read equality of the complete `MarketDataEvent`;
- idempotent repeated writes;
- same canonical identity with different `received_at` retains the first persisted event;
- exact Decimal round-trip;
- timezone-aware datetime round-trip.
