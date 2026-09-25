# ADR 0009 — G03 Reverse/Static Guard Coverage for Frozen Contracts

- Status: Accepted
- Date: 2026-09-24
- Gate: G03 Architecture & Dependency / Contract Verification
- Scope: Canonical frozen contract data models

## Decision

G03 treats reverse/static immutability verification as a general requirement for every canonical frozen contract data model in the audited inventory.

For each in-scope frozen contract:

1. A declaration guard must verify `__dataclass_params__.frozen is True`.
2. A runtime mutation guard must attempt one invalid field mutation and require `FrozenInstanceError`.
3. The test may use a narrowly scoped `cast(Any, ...)` only for the intentionally invalid runtime mutation, with an explanatory comment.
4. The inventory must explicitly enumerate every frozen contract type.
5. G03 must remain FAIL/NOT VERIFIED while any frozen contract is unenumerated or lacks the required reverse/static guards.

Current canonical inventory:

- IndicatorRequest
- IndicatorOutput
- RegimeRequest
- RegimeOutput
- CompositionRequest
- CompositionOutput
- StrategyRequest
- StrategyOutput
- ProvenanceMetadata
- DecisionRequest
- DecisionOutput
- RiskRequest
- RiskOutput
- MarketEvent

## Threat-model boundary

Frozen dataclasses provide the declared runtime immutability boundary, but Python permits an explicit `object.__setattr__` bypass. This ADR does not classify that bypass as a G03 defect because hostile in-process mutation resistance is outside the current contract threat model. If the threat model changes, the contract must be strengthened and separately tested.

This immutability rule does not establish payload/content immutability for nested mappings or sequences. Payload integrity and tamper resistance remain separate controls.

## Inventory closure criterion

The G03 audit inventory is closed only when every repository Python file in scope is:

- covered by an executable verification,
- explicitly excluded with a documented reason, or
- tracked as an accepted finding with a defined remediation action.

No gate may be marked PASS on the basis of an incomplete inventory.

## Evidence

The executable reverse/static guards are implemented in `tests/contract/test_frozen_contracts.py`. MarketEvent retains its dedicated contract-level guard as additional boundary-specific evidence.

The registry reconciliation validator is `validation/contract_registry_validator.py`. G03 executes its reconciliation through the contract test suite, and the validator writes `evidence/G03_CONTRACT_REGISTRY_RECONCILIATION.json`.

The validator fails when a registry target is unresolvable, a frozen target is absent from the executable inventory, a non-frozen target lacks an ADR reason, or an inventory entry is absent from the registry signatures.


## Registry reconciliation

Every registry target is classified independently:

| contract_id | classification / reason |
|---|---|
| ingestion_provider_boundary | MarketDataProvider is a behavioral runtime protocol; MarketEvent is separately registered as the frozen value contract |
| market_data_event | MarketEvent is a frozen canonical value contract |
| provenance_metadata | ProvenanceMetadata is a frozen canonical value contract |
| temporal_event_boundary | Pure validation callables are behavioral functions, not frozen value contracts |
| validation_result | Conceptual validation boundary is intentionally non-frozen until an executable value contract is introduced; implementation binding remains NOT VERIFIED |
| indicator_execution_boundary | Indicator is a behavioral protocol; IndicatorRequest and IndicatorOutput are frozen value contracts |
| regime_classification_boundary | RegimeClassifier is a behavioral protocol; RegimeRequest and RegimeOutput are frozen value contracts |
| signal_composition_boundary | SignalComposer is a behavioral protocol; CompositionRequest and CompositionOutput are frozen value contracts |
| strategy_evaluation_boundary | Strategy is a behavioral protocol; StrategyRequest and StrategyOutput are frozen value contracts |
| decision_evaluation_boundary | DecisionRequest and DecisionOutput are frozen canonical value contracts |
| risk_evaluation_boundary | RiskRequest and RiskOutput are frozen canonical value contracts |
| decision_evaluation_boundary | DecisionRequest and DecisionOutput are frozen canonical value contracts |
| risk_evaluation_boundary | RiskRequest and RiskOutput are frozen canonical value contracts |

The executable validator is the enforcement point for this table; this ADR is the human-readable rationale source.

## In scope

- Frozen declaration: the contract type must declare `dataclass(frozen=True)`.
- Runtime mutation: an ordinary field mutation through the instance attribute boundary must raise `FrozenInstanceError`.
- Inventory: every canonical frozen contract is explicitly enumerated by the executable G03 test.

## Out of scope

- `object.__setattr__` bypass: Python explicitly permits this low-level bypass; it is outside the current G03 contract boundary.
- `__dict__` mutation: not a G03 requirement. Slotted contracts do not expose a normal instance `__dict__`; any stronger anti-tamper property belongs to a separate security requirement.
- Metaclass or interpreter-level tampering: outside the application contract boundary.
- Pickling/unpickling reconstruction: serialization integrity is not established by frozen dataclasses and is outside G03; if serialized state crosses a trust boundary, G06 must define the required integrity/authenticity control.
- Nested payload mutation: frozen dataclasses do not recursively freeze mappings/sequences. Payload/content integrity is a separate contract/security control.

## Revisit condition

If the trust boundary is expanded to include adversarial in-process code, untrusted deserialization, hostile plugin/provider code, or tamper-evident/tamper-resistant object state, this ADR must be revised before the next G03 PASS and G06 must define and verify the stronger security invariant. G03 remains responsible only for the declared frozen-contract boundary.

G06 is explicitly responsible for covering the threats excluded here: object.__setattr__ bypasses, __dict__ tampering where applicable, deserialization reconstruction/integrity, hostile plugin/provider mutation, and any required anti-tamper property. If G06 does not verify those controls, they remain an open security gap and cannot be treated as covered merely because G03 excludes them.

## Checklist for every new frozen contract

When a new canonical frozen contract is introduced:

1. Add the type to the authoritative G03 inventory in `tests/contract/test_frozen_contracts.py`.
2. Add a valid constructor case to `_valid_instance()`.
3. Ensure the declaration guard covers it.
4. Ensure the runtime mutation guard covers it through `assert_frozen()`.
5. Update this ADR inventory and the Gap Register if the scope changes.
6. Run G01 and G02, then G03 and G04; a new SHA restarts the applicable gate chain.
