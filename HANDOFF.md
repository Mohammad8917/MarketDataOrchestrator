# Handoff — Current Verification State

**Historical baseline:** `083d29baafeae8008307e524497a5f2213bb8fff`

**Current candidate:** `4a0769a57371b5c44ca8aa1d1c7e4eb492839e01` — G04 header-schema fix in progress; not VERIFIED.

## SHA History

- `083d29b`: superseded — baseline candidate
- `41929be`: superseded — initial HANDOFF candidate
- `d621c7a`: superseded — GAP-001 in progress
- `6ccf4e2`: superseded — SMA formatting
- `3fd9ce8`: **FAILURE** — G03 failed on a legacy UUID4 fixture; G04 failed on contract-registry parsing.
- `47a24b1`: **FAILURE** — G03 passed; G04 failed on canonical source-header validation for `backtest/engine.py` and `shared/contracts/equity_curve.py`.
- `4a0769a`: current fix chain — canonical headers restored; G04 rerun pending.

> A SHA is not a baseline merely because it is newer. Baseline status requires all applicable verification gates to pass.

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
- G03 on `47a24b1` completed successfully.
- The compliance-registry step of G04 on `47a24b1` completed successfully with the six-contract baseline.

### Explicitly Pending

- G04 architecture dependency verification after the header-schema fix.
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
