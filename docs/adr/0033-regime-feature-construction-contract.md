# ADR-0033: Regime Feature Construction Contract

- Status: Accepted
- Date: 2026-09-29
- Architecture: Frozen v1.0

## Context

ADR-0032 defines a deterministic regime classifier that consumes two normalized scalar features, trend_score and volatility_score. It deliberately does not define how those scores are constructed.

The repository contains reusable indicators, but no canonical contract currently defines how market observations become regime features. Implementing that construction ad hoc would silently introduce methodology, normalization, warm-up, or temporal assumptions.

## Decision

Define a dedicated, implementation-neutral regime feature boundary at regime/features/regime_features.py.

The boundary has two responsibilities:

1. carry point-in-time regime feature inputs and provenance;
2. carry the normalized feature set consumed by the canonical regime classifier.

The canonical feature set contains exactly these required scalar semantics:

- trend_score: finite numeric value in [-1, 1]. Positive values represent upward directional evidence, negative values downward directional evidence, and zero no directional evidence.
- volatility_score: finite numeric value in [-1, 1]. Positive values represent higher-volatility evidence, negative values lower-volatility evidence, and zero no volatility-side evidence.

These scores are evidence measures, not probabilities and not trade signals.

The feature boundary MUST preserve:

- UTC event time;
- UTC receipt time;
- non-empty source event identity;
- point-in-time ordering: feature observations used for an event MUST NOT have an observation time later than that event;
- immutable request/output values.

The feature contract does NOT yet choose:

- EMA/SMA/MACD/ATR/Bollinger or any other indicator;
- lookback periods;
- threshold values;
- normalization formula;
- warm-up policy beyond explicit insufficiency failure;
- multi-timeframe aggregation;
- confidence calculation;
- strategy, risk, or decision semantics.

Those choices require a later concrete feature-construction contract backed by an executable consumer and dedicated tests.

## Consumer Binding

| Module | Export | Consumer | Consumer state | Phase |
|---|---|---|---|---|
| regime/features/regime_features.py | RegimeFeatureSet and RegimeFeatureBuilder | regime/classification/rule_based_classifier.py through the canonical RegimeRequest feature fields | EXECUTABLE consumer exists; construction implementation remains future | Regime feature construction |

The classifier remains the owner of label mapping and confidence semantics. The feature boundary owns score construction semantics only when a later concrete builder contract explicitly defines them.

## Verification

- tests/contract/test_regime_features.py
- G01-G07 and mutation testing
