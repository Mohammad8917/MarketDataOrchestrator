# Contract Registry

Architecture Frozen v1.0 — authoritative Contract Registry.

The registry is the canonical source for cross-layer contracts. Duplicate or shadow registries are forbidden.

## Registry record schema

Each contract record MUST contain:

```yaml
contract_id: "<stable-snake-case-id>"
version: "<SemVer>"
owner_layer: "<layer>"
allowed_consumers: ["..."]
forbidden_consumers: ["..."]
signature: "<typed-signature-reference>"
async_mode: "ASYNC|SYNC"
error_taxonomy: ["..."]
idempotency: "<declared-semantics>"
timeout: "<declared-semantics>"
rate_limit: "<declared-semantics>"
provenance: "<required-fields>"
tests: ["..."]
status: "ACTIVE|DEPRECATED|RETIRED"
```

## Initial contract baseline

| contract_id | owner_layer | status | verification |
|---|---|---|---|
| ingestion_provider_boundary | ingestion | ACTIVE | G04_ARCHITECTURE_DEPENDENCY |
| market_data_event | domain | ACTIVE | G03_UNIT_CONTRACT |
| provenance_metadata | shared | ACTIVE | G03_UNIT_CONTRACT |
| temporal_event_boundary | temporal | ACTIVE | G07_INTEGRATION_RESILIENCE |
| validation_result | validation | ACTIVE | G03_UNIT_CONTRACT |
| indicator_execution_boundary | indicators | ACTIVE | G03_UNIT_CONTRACT |
| regime_classification_boundary | regime | ACTIVE | G03_UNIT_CONTRACT |
| signal_composition_boundary | composition | ACTIVE | G03_UNIT_CONTRACT |
| strategy_evaluation_boundary | shared | ACTIVE | G03_UNIT_CONTRACT |
| decision_evaluation_boundary | shared | ACTIVE | G03_UNIT_CONTRACT |
| risk_evaluation_boundary | risk | ACTIVE | G03_UNIT_CONTRACT |



### ingestion_provider_boundary

```yaml
contract_id: "ingestion_provider_boundary"
version: "1.0.0"
owner_layer: "ingestion"
allowed_consumers: ["core", "analysis", "backtest"]
forbidden_consumers: ["provider implementations leaking upward"]
signature: "ingestion.interfaces.market_provider.MarketDataProvider"
async_mode: "ASYNC"
error_taxonomy: ["provider-isolated exceptions", "TimeoutError", "CancelledError"]
idempotency: "fetch is read-only; event identity is event_id"
timeout: "caller-owned bounded timeout"
rate_limit: "provider-owned policy"
provenance: "event_id, provider, symbol, timeframe, event_time, received_at"
tests: ["tests/contract/test_provider_contract.py", "tests/integration/test_ingestion_service.py"]
status: "ACTIVE"
```

### market_data_event

```yaml
contract_id: "market_data_event"
version: "1.0.0"
owner_layer: "domain"
allowed_consumers: ["ingestion", "analysis", "backtest", "evidence", "persistence"]
forbidden_consumers: ["provider transport details"]
signature: "domain.market_data_event.MarketDataEvent"
async_mode: "SYNC"
error_taxonomy: ["ValueError"]
idempotency: "immutable value object"
timeout: "N/A — in-memory validation"
rate_limit: "N/A — no external I/O"
provenance: "source_event_id, source, symbol, event_time, received_at, payload_digest"
tests: ["tests/contract/test_provider_contract.py", "tests/contract/test_frozen_contracts.py"]
status: "ACTIVE"
```

### decision_evaluation_boundary

```yaml
contract_id: "decision_evaluation_boundary"
version: "1.0.0"
owner_layer: "shared"
allowed_consumers: ["decision", "risk", "output", "backtest"]
forbidden_consumers: ["ingestion.providers", "domain_adapters"]
signature: "shared.models.decision.DecisionRequest/shared.models.decision.DecisionOutput"
async_mode: "SYNC"
error_taxonomy: ["ValueError"]
idempotency: "immutable value-object boundary; no external side effects"
timeout: "caller-owned CPU budget"
rate_limit: "N/A — no external I/O"
provenance: "source_event_id, event_time, received_at"
tests: ["tests/contract/test_decision_contract.py"]
status: "ACTIVE"