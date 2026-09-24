# Handoff — Current Verification State

**Baseline candidate freeze:** `083d29baafeae8008307e524497a5f2213bb8fff`

> This SHA is the candidate baseline requested for the current CI verification cycle.
> It is not a VERIFIED release SHA. Subsequent documentation added after this baseline
> does not retroactively make the baseline verified.

## Current Vertical Slice

```
MarketDataEvent
    ↓
MarketDataStore
    ↓
[planned production consumer: BacktestEngine]
    ↓
EquityCurve
```

### Confirmed

- `MarketDataEvent` has a deterministic UUID5 identity.
- `MarketDataStore` is an executable persistence consumer.
- SQLite uses `event_id` as PRIMARY KEY.
- Duplicate writes use `INSERT OR IGNORE`.
- Decimal OHLCV values are persisted as TEXT and reconstructed as Decimal.
- Datetimes are persisted as timezone-aware ISO-8601 TEXT and normalized to UTC on read.
- Contract tests verify complete write/read equality and replay idempotency.
- ADR-014 establishes the executable-consumer-before-verification rule.
- ADR-015 establishes persistence identity, duplicate, numeric, and datetime semantics.
- ADR-016 establishes EquityCurve as the terminal output contract for the first backtesting path.

### Explicitly Pending

- G03 CI execution/evidence.
- VERIFIED status for `MarketDataEvent`.
- A production consumer of `MarketDataStore.read_all()`.
- Implementation and verification of `BacktestEngine`.
- Implementation and verification of `EquityCurve`.
- Any move to `validation_result` before its own legitimate consumer is established.

## Orphan Policy

Do not create downstream modules merely to consume an orphan.

Start from the terminal output contract and establish the producer/consumer path backward.
A test runner is a verification consumer, not a production runtime consumer.

## CI Rule

No contract is VERIFIED without successful applicable CI evidence and a frozen evidence/SHA
record. Absence of observable CI evidence means the status remains pending.
