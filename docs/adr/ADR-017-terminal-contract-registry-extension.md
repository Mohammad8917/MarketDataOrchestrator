# ADR-017: Terminal Output Registry Extension and Backtest Domain Boundary

**Status:** Accepted

## Context

ADR-016 established EquityCurve as the terminal output contract for the first backtesting
vertical slice. The frozen five-contract registry was created before that terminal contract
existed, so adding EquityCurve requires an explicit registry decision rather than silently
changing the registry.

The BacktestEngine interface also consumes the canonical domain MarketDataEvent type. The
frozen dependency map did not previously list domain as an allowed direct dependency of the
backtest layer.

## Decision

1. Extend the authoritative Contract Registry with the interface-only contract
   `equity_curve`.
2. Keep `equity_curve` **NOT VERIFIED** until a legitimate producer and applicable tests/CI
   evidence exist. Registry presence is not verification.
3. Define `EquityCurve` as a typed Protocol in `shared.contracts.equity_curve`; do not
   create a concrete dataclass or runtime implementation in this phase.
4. Define `BacktestEngine` as a typed Protocol in `backtest.engine` with:
   `run(tuple[MarketDataEvent, ...]) -> EquityCurve`.
5. Permit the backtest layer to depend directly on the canonical domain layer for this
   approved input contract. This is a frozen architecture-map amendment and is validated
   mechanically.
6. The dataflow is:
   `MarketDataStore.read_all() -> BacktestEngine.run(...) -> EquityCurve`.
   The BacktestEngine is the consumer of the MarketDataStore output; the store is not a
   consumer of BacktestEngine.
7. The existence of the Protocol establishes a typed future consumer boundary, but it does
   **not** by itself constitute an executable production consumer. `MarketDataStore`
   therefore remains ACTIVE-ORPHAN until a production BacktestEngine implementation calls
   `read_all()`.

## EquityCurve Contract

`EquityCurve` exposes aligned tuples:

- `timestamps: tuple[datetime, ...]`
- `equity: tuple[Decimal, ...]`
- `drawdown: tuple[Decimal, ...]`

Required invariants for any future implementation:

- all three tuples have equal length;
- timestamps are timezone-aware UTC datetimes;
- timestamps are monotonically non-decreasing;
- equity values are finite Decimal values;
- drawdown values are finite Decimal values and are not positive;
- each index represents one portfolio state at the corresponding timestamp.

These invariants describe the contract; they are not yet a concrete implementation.

## Consequences

- The registry now contains six canonical contracts.
- EquityCurve has a stable typed identity before implementation.
- BacktestEngine has a stable typed execution boundary before implementation.
- No synthetic runtime consumer is introduced merely to close the orphan.
- The existing MarketDataStore orphan status remains explicit until executable production
  consumption exists.
