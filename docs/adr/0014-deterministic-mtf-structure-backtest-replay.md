# ADR 0014 — Deterministic Multi-Timeframe Structure Backtest Replay

## Status
Accepted

## Date
2026-10-02

## Scope
Replay the canonical multi-timeframe structure alignment methodology against historical point-in-time requests.

## Contract
- `backtest_mtf_structure_replay_boundary` v1.0.0
- Producer: `backtest.mtf_structure_replay.MtfStructureReplay`
- Integration: `backtest.replay_engine.BacktestReplayEngine`

## Rules
1. Requests MUST be strictly increasing by event time.
2. The replay consumer MUST delegate each request exactly once to the supplied `MtfStructureEvaluator`.
3. Output event time MUST equal the request event time.
4. Output source event ID MUST equal the request source event ID.
5. Results MUST be returned as an immutable tuple.
6. The replay consumer MUST perform no provider I/O, persistence mutation, cost analysis, risk evaluation, or trading/decision finalization.
7. Historical replay MUST use the same executable evaluator boundary as live analytical composition; replay is not a second methodology.

## Multi-market scope
The boundary is market-agnostic and applies equally to Crypto, Forex, and Gold. No provider-specific or asset-class-specific behavior is encoded.

## Rationale
A backtest must reconstruct what the MTF structure layer could have observed at each historical event time without introducing future information or a replay-only analytical implementation.

## Out of scope
- Structure detection methodology
- Signal composition
- Cost/liquidity/slippage
- Risk
- Decision finalization
- Execution
