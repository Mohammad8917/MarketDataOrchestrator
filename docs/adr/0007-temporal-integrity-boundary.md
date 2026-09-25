# ADR-0007: Temporal Integrity Boundary

- Status: Accepted
- Date: 2026-09-24
- Architecture: Frozen v1.0

## Decision

Temporal validation is centralized at the validation boundary. Provider/event timestamps remain distinct from local receipt timestamps. Persisted boundary timestamps are explicit UTC values; elapsed durations use monotonic readings.

## Rules

- event_time must not be later than received_at;
- timestamps must be timezone-aware UTC;
- provider/local clock skew has an explicit threshold;
- negative or reversed monotonic readings are rejected;
- the validator performs no external I/O and never fabricates timestamps.

## Release rule

Temporal behavior remains release-blocking until its contract, tests, coverage, architecture verification, and CI gate evidence are all valid.
