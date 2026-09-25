# ADR 0017 — Runtime Consumer Definition

- Status: Accepted
- Date: 2026-09-24
- Gate: G03
- Scope: Formal definition of a runtime consumer for frozen contract governance and consumer audit

## Decision

A **consumer** is any production runtime reader that receives an instance of a frozen contract and performs at least one operation on that instance.

This is the strict **Runtime Reader** definition.

The definition applies uniformly across all layers and does not distinguish between internal orchestration, ingestion handling, or cross-layer processing when the code actually reads and processes the contract instance.

## Rules

1. A runtime reader MUST be production code, not test code.
2. A runtime reader MUST receive or obtain a contract instance through an executable runtime path.
3. The reader MUST perform at least one operation on the contract instance; import-only, annotation-only, declaration-only, or type-check-only references do not qualify.
4. Test doubles, mocks, fixtures, test-only helpers, and test consumers are not runtime consumers.
5. Protocols, interfaces, dataclass declarations, registries, manifests, and documentation are not consumers.
6. Internal ingestion/orchestration code is a consumer when it reads and processes the contract instance.
7. Every current runtime consumer MUST be represented in the contract's `allowed_consumers` registry field.
8. A runtime consumer that is absent from `allowed_consumers` is a G03 contract-governance finding.
9. A registry consumer for which no current runtime reader exists is not evidence of a current consumer. It remains a future-consumer declaration and MUST be distinguished from current runtime evidence.
10. Consumer status MUST NOT be manufactured solely to satisfy CI. Future consumers remain future consumers until executable runtime evidence exists.

## Evidence standard

Consumer claims require executable runtime data-flow evidence.

The minimum evidence is:

- source file containing the runtime reader;
- contract type or instance reference;
- operation performed on the instance;
- a production execution path connecting the contract to the reader.

A bare import, return annotation, protocol declaration, registry entry, or test reference is insufficient.

## Consequence for MarketEvent

`ingestion.IngestionService` is a current runtime consumer of `MarketEvent` because it receives provider results containing `MarketEvent` instances and reads/processes those instances while collecting, ordering, and returning the event stream.

Therefore `market_data_event.allowed_consumers` MUST include `ingestion`.

This is a registry reconciliation change, not an implementation workaround.

## Consumer audit status vocabulary

The canonical audit uses these statuses:

- `ACTIVE-CONSUMER`: current production runtime reader with executable evidence.
- `ACTIVE-ORPHAN`: current contract/output exists but no downstream runtime consumer is evidenced.
- `FUTURE-CONSUMER`: registry/architecture identifies a future consumer, but no current executable runtime reader exists.

A fourth status, `REGISTRY-REMOVE CANDIDATE`, may be used when a registry declaration has no architectural justification and is not merely a future binding.

## G03 enforcement boundary

This ADR establishes the semantic rule. The initial implementation records the audited baseline in `evidence/G03_CONSUMER_MATRIX.json`.

Future automated enforcement MAY add AST/data-flow checks, but such tooling MUST preserve the same semantics and MUST NOT classify imports, protocols, tests, or declarations as consumers.

## Interaction with ADR 0014

ADR 0014 remains authoritative for export/consumer binding and the rule that a future consumer is not a current runtime consumer.

ADR 0017 supplies the precise operational definition of "consumer" used by that rule.

## Revisit condition

Revisit this ADR only if the architecture adopts a different formal execution model that makes runtime data-flow insufficient to establish contract consumption, or if the frozen contract governance model changes.
