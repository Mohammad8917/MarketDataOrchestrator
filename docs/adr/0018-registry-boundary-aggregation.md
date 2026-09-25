# ADR 0018 — Registry Boundary Aggregation of Frozen Types

- Status: Accepted
- Date: 2026-09-24
- Gate: G03
- Scope: Frozen contract inventory ↔ Contract Registry cardinality
- Supersedes: None

## Context

The frozen-contract inventory contains 14 frozen type entries, while the authoritative Contract Registry contains 11 registry boundary entries.

These counts are intentionally not one-to-one. A registry entry represents a contract boundary, and one boundary may canonically govern more than one frozen value type belonging to the same executable interface. Therefore, subtracting registry-entry count from frozen-type count is not a valid missing-contract test.

The executable reconciliation evidence is authoritative for this relationship. It currently reports:

- frozen inventory entries: 14
- registry boundary entries: 11
- reconciliation findings: none
- reconciliation status: PASS

## Decision

The registry will remain boundary-oriented rather than type-oriented.

A single registry boundary MAY map to multiple frozen value types when those types constitute the request/output value side of one canonical behavioral boundary.

The reconciliation validator MUST compare the actual typed targets of each registry boundary against the frozen inventory. It MUST NOT require frozen-type count to equal registry-boundary count.

A frozen type is considered covered when it is explicitly targeted by the appropriate registry boundary. A registry boundary may additionally reference a non-frozen behavioral protocol or callable when the architecture intentionally treats that target as a behavioral boundary rather than a frozen value contract; the non-frozen rationale must be explicit.

## Canonical example

indicator_execution_boundary is one registry boundary:

indicator_execution_boundary -> [Indicator, IndicatorRequest, IndicatorOutput]

Within that mapping:

- Indicator is a structural `typing.Protocol`, not a value-object/dataclass contract. It declares the executable `calculate(request) -> output` shape and class-level contract metadata, but it does not define a canonical instance state that must be immutable.
- Indicator is therefore intentionally non-frozen: concrete indicator implementations are behavioral bindings to this protocol, while the request/output value objects are the frozen data contracts.
- IndicatorRequest is frozen.
- IndicatorOutput is frozen.

This is an explicit registry-boundary exception, not an accidental omission. The non-frozen target is justified by its declaration in `indicators/core/base.py` as `@runtime_checkable class Indicator(Protocol)`, and by the registry signature in `docs/contracts.md`, which names the protocol together with the two frozen value types. The frozen inventory test enumerates the canonical frozen value types and does not enumerate `Indicator`, confirming that the governance baseline treats it as behavioral rather than a frozen value contract.

Thus one registry boundary legitimately accounts for two frozen value types.

The same aggregation pattern applies to other boundaries, including:

- regime_classification_boundary -> [RegimeRequest, RegimeOutput]
- signal_composition_boundary -> [CompositionRequest, CompositionOutput]
- strategy_evaluation_boundary -> [StrategyRequest, StrategyOutput]
- decision_evaluation_boundary -> [DecisionRequest, DecisionOutput]
- risk_evaluation_boundary -> [RiskRequest, RiskOutput]

market_data_event and ingestion_provider_boundary may both reference the same frozen MarketEvent type because they represent distinct architectural boundaries around the same canonical value object. This is not duplicate ownership of the frozen type.

## Governance rule

The following is a G03 defect:

- a frozen type has no authoritative registry target;
- a registry target points to a frozen type that is absent from the inventory;
- a registry boundary has an unjustified or undocumented non-frozen target;
- the committed reconciliation artifact differs from validator-generated evidence.

The following is not a defect by itself:

- 14 frozen type entries versus 11 registry boundaries.

## Evidence

Authoritative evidence:

- docs/contracts.md
- tests/contract/test_frozen_contracts.py
- validation/contract_registry_validator.py
- evidence/G03_CONTRACT_REGISTRY_RECONCILIATION.json

The reconciliation artifact is the executable result and currently records findings: [] and status: PASS.

## Consequence

The registry remains compact and boundary-oriented while the frozen inventory remains type-oriented. Future contract additions must update both the typed inventory and the appropriate registry boundary mapping; a new boundary is not required merely because another frozen request/output type is introduced within an existing canonical boundary.

## Revisit condition

Revisit this ADR only if the governance model changes from boundary-oriented contracts to one-registry-entry-per-frozen-type semantics.
