# ADR-016: Output Contract and Runtime Direction

**Status:** Accepted

## Decision

The system's first defined end-to-end trading output contract is **EquityCurve**.

The intended runtime direction is:

```
MarketDataEvent
    ↓
MarketDataStore.read_all()
    ↓
BacktestEngine
    ↓
EquityCurve
```

The dependency direction is therefore defined from the final observable output backward:

- **EquityCurve** is the terminal runtime artifact for the first backtesting vertical slice.
- **BacktestEngine** is the producer of EquityCurve and consumes replayed canonical market events.
- **MarketDataStore** provides persisted/replayed MarketDataEvent values to the BacktestEngine.
- **MarketDataEvent** remains the canonical market-data domain input.

## EquityCurve Definition

`EquityCurve` is an interface-only terminal output contract defined by
`shared.contracts.equity_curve.EquityCurve`.

It exposes:

- `timestamps: tuple[datetime, ...]`
- `equity: tuple[Decimal, ...]`
- `drawdown: tuple[Decimal, ...]`

Future implementations MUST keep these sequences aligned and equal in length; timestamps
must be timezone-aware UTC values in non-decreasing order; equity and drawdown values must be
finite Decimal values; drawdown values must not be positive.

The protocol is intentionally not a concrete dataclass or runtime implementation in this phase.

## Scope

This ADR establishes runtime direction and ownership intent; it does **not** claim that
BacktestEngine or EquityCurve are implemented or verified.

The next implementation step for this path MUST establish the contracts and ownership of
BacktestEngine and EquityCurve before production implementation is added.

## Consumer Rule

A module is not considered justified merely because another module can consume it.

For the first vertical slice, every runtime component must have a defined role in the path to
the terminal EquityCurve output. Components that cannot be connected to this path by a
legitimate producer/consumer relationship must remain unimplemented or be recorded as
orphans rather than being created speculatively.

The test suite may verify a component, but test execution alone is not a production runtime
consumer.

## Consequences

- The project will not resolve orphan chains by blindly adding another downstream module.
- New runtime components must be justified by their position in the path to EquityCurve.
- `MarketDataStore` now has a defined intended production consumer: `BacktestEngine`,
  but remains **ACTIVE-ORPHAN** until that consumer exists in executable production code.
- `BacktestEngine` and `EquityCurve` are not to be marked VERIFIED merely because this
  ADR defines them.
- Any change to the terminal output contract requires an explicit ADR and review of the
  affected dependency path.
