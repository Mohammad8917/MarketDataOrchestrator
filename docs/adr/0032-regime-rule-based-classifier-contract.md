# ADR-0032: Deterministic Rule-Based Regime Classifier

- Status: Accepted
- Date: 2026-09-29
- Architecture: Frozen v1.0

## Context

ADR-0002 defines the canonical regime boundary and ADR-0031 defines its labels. An executable classifier still requires explicit feature semantics, precedence, and confidence rules.

## Decision

Implement a deterministic baseline classifier at `regime/classification/rule_based_classifier.py`.

The request MUST contain two named scalar features:

- `trend_score`: finite numeric value in [-1, 1]. Negative means downward directional evidence; positive means upward directional evidence; zero means no directional evidence.
- `volatility_score`: finite numeric value in [-1, 1]. Negative means lower-volatility evidence; positive means higher-volatility evidence; zero means no volatility-side evidence.

Classification precedence is deterministic:

1. `trend_score > 0` → `trend_up`.
2. `trend_score < 0` → `trend_down`.
3. `trend_score == 0` and `volatility_score < 0` → `range_low_volatility`.
4. `trend_score == 0` and `volatility_score > 0` → `range_high_volatility`.
5. Both scores equal zero → `unknown`.

Confidence is the absolute value of the score that determined the label; `unknown` has confidence 0.0.

The classifier is point-in-time and performs no external I/O. It does not construct the scores, use future observations, select strategies, size positions, or make risk decisions.

This is a versioned deterministic baseline, not a claim that these features are the only valid market-regime model.

## Verification

- `tests/contract/test_rule_based_regime_classifier.py`
- `tests/contract/test_regime_contract.py`
- G01-G07 and mutation testing
