# ADR-0034: Deterministic Regime Feature Methodology Contract

- Status: Accepted
- Date: 2026-09-29
- Architecture: Frozen v1.0

## Context

ADR-0033 defines the boundary and normalized semantics of trend_score and volatility_score, but deliberately leaves their construction methodology unspecified.

## Decision

Define a deterministic, point-in-time baseline methodology using close prices only.

### Inputs

RegimeFeatureRequest MUST provide:
- strictly increasing UTC observation timestamps;
- one positive, finite close price for each timestamp;
- final observation timestamp equal to event_time;
- trend_lookback >= 2;
- volatility_short_lookback >= 2;
- volatility_long_lookback > volatility_short_lookback.

Lookbacks count completed observations, including event_time.

### Trend score

For the last trend_lookback closes, compute adjacent close-to-close log returns:
r_i = ln(close_i / close_(i-1)).

Convert each return to sign: -1, 0, or +1.

trend_score = sum(sign(r_i)) / (trend_lookback - 1).

The result is bounded to [-1, 1]. Positive values represent upward directional persistence; negative values represent downward directional persistence; zero means no net directional evidence. Return magnitude does not affect this score.

### Volatility score

For the final short and long observation windows, compute mean absolute close-to-close log return.

Let S be the short-window mean and L the long-window mean.

If S + L > 0:
volatility_score = (S - L) / (S + L).

If S = L = 0, volatility_score = 0.

The result is bounded to [-1, 1]. Positive values mean higher short-window volatility than the long-window baseline; negative values mean lower volatility; zero means equal volatility or no movement.

### Warm-up and temporal integrity

Insufficient history MUST fail deterministically with ValueError.

No future observation may participate in either score. The final observation is the point-in-time boundary.

The methodology performs no provider I/O, persistence mutation, strategy selection, trading decision, risk decision, or external state access.

### Versioning

- Contract ID: regime_feature_methodology
- Contract version: 1.0.0
- Methodology ID: deterministic_close_return_baseline
- Methodology version: 1.0.0

Any formula or lookback-semantic change requires a new version/ADR.

## Consequences

The project now has an explicit reproducible baseline from market observations to canonical normalized scores.

This is a baseline methodology, not a claim that it is the only valid market-regime model. Indicator-based, multi-timeframe, adaptive, probabilistic, or machine-learning methods remain separate future contracts and MUST NOT silently alter this methodology.
