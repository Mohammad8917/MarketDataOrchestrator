# ADR 0039: Deterministic Setup Methodology v1

- **Status:** Accepted
- **Date:** 2026-10-02
- **Scope:** Setup evaluation
- **Contract:** `setup_evaluation_boundary` v1.0.0
- **Methodology:** `deterministic_directional_setup_v1` v1.0.0

## Decision

Define the first executable setup methodology as a deterministic directional classification over normalized analytical evidence.

For input values in [-1, 1]:

1. Compute the arithmetic mean.
2. Classify **bullish** when the mean is at least 0.5.
3. Classify **bearish** when the mean is at most -0.5.
4. Otherwise classify **neutral**.
5. Set strength to the absolute mean.

## Boundaries

This methodology is market-agnostic and applies equally to Crypto, Forex, and Gold. It contains no provider, persistence, execution, cost, liquidity, risk, confirmation, or decision ownership.

The threshold is a deterministic v1 engineering rule, not a claim of statistical optimality or profitability. Calibration and empirical evaluation belong to later validation work.

## Revisit

Revisit only when evidence from the setup evaluation/backtest slices demonstrates a need for a versioned methodology change.
