# ADR 0014 — Module Export and Consumer Binding Before Implementation

- Status: Accepted
- Date: 2026-09-24
- Gate: G03/G04
- Scope: Every new production implementation, beginning with the indicator layer

## Decision

A production module MUST NOT be implemented solely because its path exists in the frozen tree.

Before implementation, the module MUST have a durable binding record that identifies:

1. the exported behavior/type/contract;
2. the authoritative consumer;
3. the architectural layer and allowed dependency direction;
4. whether the consumer is already executable or is a declared future consumer;
5. the phase in which the consumer becomes executable;
6. the contract that prevents later API drift.

A future consumer is not counted as a current runtime consumer.

If a module has no justified consumer in the frozen architecture, implementation work stops and the module is a design/scope finding rather than an implementation task.

## Current scope finding

The phase manifest currently contains 428 active skeleton entries before package-boundary cleanup: 398 production and 30 test modules.

Seventy-three active package initializers were reviewed as package-boundary files with no executable runtime behavior and reclassified to P0/EXCLUDED. This is a scope correction, not an implementation bypass.

The resulting active skeleton scope is 355 entries:

- 325 production implementation skeletons;
- 30 executable test skeletons.

The current production tree also contains large capability groups whose executable downstream consumers do not yet exist. This is a design/scope finding, not permission to manufacture consumers.

## SMA binding

| Module | Export | Consumer | Consumer state | Phase |
|---|---|---|---|---|
| indicators/trend/sma.py | SimpleMovingAverage implementing indicator_execution_boundary | Future strategy/analysis consumer through the canonical Indicator protocol | NOT YET EXECUTABLE | P1 contract slice; consumer activation follows strategy/analysis implementation |

SMA therefore remains an intentionally isolated implementation at this stage. It MUST NOT acquire strategy-specific dependencies or an invented direct strategy API merely to create a consumer.

The canonical registry binding is the generic `indicator_execution_boundary`; a separate registry entry for every algorithm is not required when the concrete implementation structurally binds to that protocol. A concrete algorithm without an executable consumer remains an explicitly tracked orphan until its consumer phase is implemented.

## Implementation rule

For each subsequent production module, the implementation change MUST be preceded or accompanied by its binding record in this ADR or a later ADR dedicated to the module/group.

The binding record MUST be updated when the consumer becomes executable. A module MUST NOT be refactored later merely to satisfy an undocumented consumer assumption.

## 4H temporal use

No indicator implementation is considered 4H-specific merely because it can process four-hour candles.

For SMA, the time-frame boundary is owned by the upstream market-data/analysis request. SMA consumes an ordered series plus the request event timestamp; it does not fetch or infer a 4H timeframe itself.

The eventual 4H strategy/analysis consumer MUST provide a correctly aggregated/selected 4H series and MUST bind its time semantics through the existing temporal and indicator contracts.

## Revisit condition

If the strategy/analysis contract requires a different indicator input/output shape, that is a contract evolution event. It requires an ADR, contract-version decision, consumer migration plan, and fresh G01 through applicable-gate evidence.


## Decision rule: interface-first for future consumers

This ADR selects **Interface-First** for modules whose justified consumer is in a later phase.

Before such a module receives an implementation, its stable boundary MUST be frozen as a typed interface/protocol or canonical contract: exported names, input/output types, semantic invariants, temporal semantics, failure behavior, and version. The future consumer is designed against that boundary rather than against an uncommitted implementation detail.

An implementation MAY proceed before the consumer is executable only when that interface-first record exists and the module has a justified future consumer. The implementation is then an `active-orphan` runtime component: active, tested, but intentionally not yet connected to an executable downstream path.

If the eventual consumer requires a different boundary, the change is contract evolution: new ADR/contract version, consumer migration/review, and fresh applicable-gate evidence are mandatory. Silent API refactoring is prohibited.

If no justified future consumer or stable interface can be established, the implementation-waits rule applies: do not implement the module; keep it as an architecture/scope finding.

## SMA binding status — speculative interface

The current SMA interface is **speculative**, not derived from an executable strategy requirement. The repository currently contains no executable strategy consumer that imports or calls `SimpleMovingAverage`; the strategy boundary only defines generic `StrategyRequest.inputs: Mapping[str, float]` and does not specify an SMA dependency.

Therefore `indicator_execution_boundary@1.0.0` is a frozen indicator-layer contract, but it is **not evidence that the future strategy will require this exact SMA API**. The SMA implementation remains active-orphan.

The current SMA semantics are explicitly **final-window, single-value output**, not a rolling output series: for an ordered close series and period `p`, only the final `p` values are averaged and returned as `IndicatorOutput.values["sma"]`. The known-value reference `[1,2,3,4,5]` with period `3` therefore yields `4.0`; it does not imply a rolling result `[2.0,3.0,4.0]`. A future consumer requiring rolling outputs would constitute a contract-evolution event and MUST NOT be introduced by changing the test alone. When the strategy/analysis phase begins, the first consumer design review MUST explicitly verify whether SMA's current interface is required. If not, contract evolution or replacement is handled through the normal ADR/contract process; no compatibility assumption may be treated as proven in advance.
