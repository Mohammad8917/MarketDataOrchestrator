# ADR-0004: Canonical Strategy Evaluation Contract

- Status: Accepted
- Date: 2026-09-24
- Architecture: Frozen v1.0

## Context

The strategy subsystem contained definitions, selectors, execution, and evaluation modules as skeletons but lacked one typed boundary that could be verified independently of concrete strategy algorithms.

## Decision

Define `strategy_evaluation_boundary` version `1.0.0` through `shared.interfaces.strategy.Strategy`.

The contract carries:
- source event identity;
- UTC event and receipt timestamps;
- named upstream inputs;
- an explicit action and bounded strength;
- strategy identity and contract version.

Concrete strategies implement `evaluate(StrategyRequest) -> StrategyOutput`. The boundary is synchronous, pure in-memory, and excludes provider I/O, persistence mutation, decision finalization, and risk ownership.

## Consequences

Strategy definitions, selectors, execution logic, and evaluation components can be implemented independently while sharing one stable typed boundary. Contract and architecture tests provide executable verification.

Concrete strategy behavior is not released merely by registering this contract; each concrete implementation remains subject to its own ownership, dependency, testing, coverage, temporal, and security gates.

## Verification

- `tests/contract/test_strategy_contract.py`
- `tests/architecture/test_strategy_single_source.py`
- Architecture/dependency validator
