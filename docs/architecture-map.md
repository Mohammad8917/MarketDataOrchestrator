# Frozen Architecture Ownership & Dependency Map

**Architecture:** Frozen v1.0  
**Source of truth:** README.md  
**Purpose:** executable support artifact for Responsibility, Ownership, Dependency Direction, and Cycle checks.

## Global rules

- Every Python file has exactly one primary responsibility.
- OWNS is limited to behavior/state/contracts directly controlled by that file.
- DOES_NOT_OWN records delegated behavior and forbidden ownership.
- Runtime dependencies must be explicit and directional.
- A dependency edge is consumer -> provider.
- Cycles are forbidden unless an explicit architecture change authorizes one; the frozen v1.0 baseline authorizes none.
- shared is the lowest business layer and MUST NOT depend upward.
- domain is independent of orchestration, providers, and higher business layers.
- app is the composition root and may depend downward; downstream layers MUST NOT depend on app.
- core is runtime orchestration and MUST NOT depend on app.

## Layer ownership and allowed dependency boundaries

| Layer | Primary responsibility | Allowed dependency layers | Forbidden ownership/dependencies |
|---|---|---|---|
| app | Composition/bootstrap/runtime wiring | core; config; shared; approved contracts | business logic; provider business logic; downstream layers importing app |
| core | Runtime orchestration, lifecycle, scheduling, resources, health | config; shared; approved lower runtime contracts | analysis; indicators; strategy; decision; risk business logic; app |
| config | Configuration loading, schema, environment, feature flags, capability configuration | shared; approved infrastructure | business layers |
| shared | Shared primitives, contracts, events, errors, models, utilities | stdlib; shared subpackages | all higher business layers |
| domain | Canonical domain semantics and market policies | shared | orchestration; providers; analysis; strategy; decision; risk |
| ingestion | Provider acquisition, normalization, validation boundary | shared; config; domain contracts; ingestion interfaces | analysis; indicators; strategy; decision; risk; persistence policy |
| domain_adapters | Provider/market representation -> canonical domain | domain; ingestion interfaces; shared | analysis; strategy; decision; risk; persistence |
| indicators | Reusable indicator primitives | shared; approved domain primitives | analysis duplication; strategy; decision; risk; provider I/O |
| analysis | Market-data interpretation and analysis | indicators; domain; canonical ingestion data; shared | strategy execution; decision; risk; provider I/O |
| regime | Regime detection/classification/transition | analysis; indicators; domain; shared | strategy execution; decision finalization; risk; provider I/O |
| composition | Signal combination/weighting/voting/consensus | indicators; analysis; regime; shared contracts | decision finalization; risk; persistence; provider I/O |
| strategy | Strategy definition/selection/evaluation/execution | analysis; regime; composition; shared contracts; backtest for research-only evaluation | evidence finalization; decision; risk; signal persistence |
| evidence | Evidence graph/scoring/independence/conflict | analysis; composition; regime; strategy; shared contracts | final decision; risk; provider I/O; persistence mutation |
| decision | Decision construction from validated evidence/context | evidence; strategy/context contracts; regime; shared contracts | risk implementation; provider I/O; persistence; output |
| risk | Independent risk assessment/sizing/limits | decision; domain; shared contracts; approved config | strategy selection; evidence generation; provider I/O; output |
| persistence | Storage/repository/snapshot/migration boundary | shared; approved domain artifacts | provider transport; strategy/decision/risk policy; output formatting |
| feedback | Outcome/performance/calibration feedback | backtest; persistence; shared outcome contracts | live strategy mutation; decision/risk mutation; provider I/O |
| output | Formatting/delivery/notification boundary | shared signal/decision contracts; notifier interfaces | decision generation; risk calculation; provider acquisition; persistence policy |
| validation | Cross-layer validation and compliance gates | canonical upstream contracts; shared | provider business logic; strategy generation; persistence mutation; output formatting |
| backtest | Historical replay/evaluation/research | ingestion; indicators; analysis; regime; composition; strategy; evidence; decision; risk; validation; domain; shared | future-data leakage; provider credentials; production side effects; live feedback mutation |

## Baseline dependency direction

The intended high-level direction is:

app -> core -> {config, ingestion, persistence, validation, output, and approved runtime contracts}

Within the business pipeline:

ingestion -> domain_adapters -> domain/shared

domain/shared -> indicators -> analysis -> regime -> composition -> strategy -> evidence -> decision -> risk

persistence consumes approved canonical artifacts and does not own business policy.

feedback consumes historical outcomes and persistence/backtest evidence; it does not mutate live strategy/decision/risk state.

backtest may consume the analysis/decision stack for research, but must remain isolated from production side effects.

No downstream layer may import its upstream consumer. In particular:
- core -> app is forbidden.
- shared -> any higher business layer is forbidden.
- domain -> ingestion/analysis/strategy/decision/risk is forbidden.
- risk -> strategy/evidence/output is forbidden.
- decision -> risk is forbidden.
- strategy -> decision/risk is forbidden.
- evidence -> decision/risk is forbidden.
- analysis -> strategy/decision/risk is forbidden.

## File-level declaration requirement

The per-file header remains authoritative for the file's exact responsibility, ownership, and direct dependency declaration. This map defines the frozen layer-level boundary and cycle policy; it does not replace the required file header.

Any disagreement between a file declaration and the frozen layer boundary is a compliance failure and MUST be resolved before the file is considered verified.
