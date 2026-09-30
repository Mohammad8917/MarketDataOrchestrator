# ADR-0035: Deterministic Market Structure Methodology Contract

- Status: Accepted
- Date: 2026-09-30
- Architecture: Frozen v1.0

## Context

PR #46 establishes the canonical market-agnostic Market Structure boundary and vocabulary, but intentionally leaves detection methodology unspecified.

## Decision

Define a project-owned deterministic baseline methodology, versioned independently from future methodology variants.

### Methodology identity

- Methodology ID: `deterministic_confirmed_pivot_structure`
- Methodology version: `1.0.0`
- Contract ID: `market_structure_boundary`
- Contract version: `1.0.0`

### Inputs and confirmation

The implementation consumes the existing `MarketStructureRequest` point-in-time OHLCV observations.

- `pivot_left_bars = 2`
- `pivot_right_bars = 2`
- A swing high is strictly greater than every high in its configured left and right confirmation windows.
- A swing low is strictly lower than every low in its configured left and right confirmation windows.
- A pivot becomes observable only after the full right confirmation window has elapsed.
- Equal highs/lows do not qualify as a strict pivot.

### Structural labels

For confirmed highs:
- above the previous confirmed high => HH
- otherwise => LH

For confirmed lows:
- above the previous confirmed low => HL
- otherwise => LL

### Structural events

- breakout: point-in-time close is strictly above the latest confirmed swing-high level.
- breakdown: point-in-time close is strictly below the latest confirmed swing-low level.
- structure shift: a breakout follows a bearish structural sequence, or a breakdown follows a bullish structural sequence.

These are descriptive events, not trading instructions.

### State

Use equal-length state windows with:

- `state_lookback = 10`
- expansion ratio = 1.25
- compression ratio = 0.75

For each state window, width is `max(high) - min(low)`.

- current width / previous equal-length width >= 1.25 => expansion
- current width / previous equal-length width <= 0.75 => compression
- otherwise => range

Insufficient history MUST fail deterministically.

### Temporal integrity

No future observation may participate in a point-in-time result. A pivot requiring right-side confirmation is reported only when that confirmation data has become available.

### Market scope

The baseline is deliberately identical for Crypto, Forex, and Gold. No funding, futures, order-book, exchange, broker, or provider assumption is introduced.

Any market-specific adaptation requires a new, explicitly versioned methodology rather than hidden branching inside the baseline.

### Exclusions

The methodology does not own:
- BUY/SELL decisions
- position sizing
- risk management
- execution
- provider I/O
- persistence mutation
- strategy finalization

## Consequences

Market Structure now has a reproducible project-owned baseline that can be implemented and backtested without silently changing definitions. Future indicator-based, multi-timeframe, adaptive, probabilistic, or ML structure methods remain separate versioned methodologies.
