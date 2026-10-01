# ADR 0012 — Backtest Market Structure Replay Integration

- **Status:** Accepted
- **Date:** 2026-10-01
- **Scope:** Market Structure → Methodology → Backtest Consumer
- **Markets:** Crypto, Forex, Gold

## Decision

Market Structure is integrated into the existing Backtest subsystem through a dedicated replay consumer and the existing BacktestReplayEngine.

No parallel Backtest subsystem is introduced.

## Methodology

The executable baseline remains `deterministic_confirmed_pivot_structure` v1.0.0.

It uses confirmed pivots with:
- 2 left bars
- 2 right bars
- strict high/low comparisons
- deterministic HH/HL/LH/LL labeling
- descriptive breakout/breakdown detection from confirmed structural levels

The methodology remains descriptive only. It does not produce BUY/SELL, risk, cost, or execution semantics.

`StructureState` classification remains `None` because the configured expansion/compression parameters are not yet backed by a separately verified state-classification methodology. No implicit rule is invented.

## Backtest Consumer

`MarketStructureReplay` is the historical point-in-time consumer.

Rules:
- requests must be non-empty and strictly increasing by `event_time`
- evaluator must satisfy `MarketStructureEvaluator`
- each evaluator output must preserve request `event_time`
- each evaluator output must preserve request `source_event_id`
- outputs are immutable and ordered
- no provider I/O
- no persistence mutation
- no cost/liquidity analysis
- no risk evaluation
- no decision finalization
- no trading action

## Integration

`BacktestReplayEngine` exposes `replay_market_structure()` and delegates to `MarketStructureReplay`.

The Backtest boundary therefore carries Regime Analysis Replay, Composition Replay, Confirmation Replay, and Market Structure Replay.

All are complementary analytical replay consumers; none replaces Strategy, Decision, or Risk.

## Verification

Contract and replay tests cover methodology identity and invariants, deterministic evaluator output, point-in-time behavior, replay ordering, evaluator boundary validation, and timestamp/source-event provenance preservation.

## Consequences

Market Structure can now be replayed through the same canonical Backtest integration boundary for Crypto, Forex, and Gold without introducing Decision/Risk dependencies.

The next analytical slice remains downstream of Market Structure and upstream of Decision/Risk.