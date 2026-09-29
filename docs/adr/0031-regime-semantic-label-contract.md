# ADR-0031: Canonical Regime Semantic Labels

- Status: Accepted
- Date: 2026-09-29
- Architecture: Frozen v1.0

## Context

ADR-0002 defines the typed regime classification boundary but intentionally leaves concrete regime semantics open. The regime subsystem cannot safely implement a classifier while labels remain arbitrary strings.

## Decision

Define a minimal deterministic semantic vocabulary for the first executable regime slice:

- `trend_up`: directional upward regime.
- `trend_down`: directional downward regime.
- `range_low_volatility`: non-directional regime with lower volatility.
- `range_high_volatility`: non-directional regime with higher volatility.
- `unknown`: insufficient or invalid information for a canonical classification.

These labels are classification vocabulary only. They do not prescribe a trading decision, strategy selection, position sizing, or risk response.

Thresholds, feature construction, confidence calculation, and detector algorithms remain separate contracts and MUST NOT be inferred from these labels.

The canonical identifiers are defined once in `regime/classification/regime_labels.py`.

## Consequences

Concrete detectors can produce stable, machine-readable labels without inventing competing names. The classifier remains independent of strategy and risk layers.

This ADR intentionally does not select a statistical algorithm or numeric threshold. Those require their own explicit specification and tests.

## Verification

- `tests/contract/test_regime_contract.py`
- `tests/contract/test_regime_labels.py`
