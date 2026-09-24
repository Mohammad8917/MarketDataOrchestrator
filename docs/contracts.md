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
| provenance_metadata | evidence | ACTIVE | G03_UNIT_CONTRACT |
| temporal_event_boundary | temporal | ACTIVE | G07_INTEGRATION_RESILIENCE |
| validation_result | validation | ACTIVE | G03_UNIT_CONTRACT |

## Typed contract bindings

### market_data_event

```yaml
contract_id: "market_data_event"
version: "1.0.0"
owner_layer: "domain"
allowed_consumers: ["ingestion", "analysis", "backtest", "validation"]
forbidden_consumers: ["app", "core", "strategy", "decision", "risk", "persistence", "output"]
signature: "domain.market_data_event.MarketDataEvent"
async_mode: "SYNC"
error_taxonomy: ["TypeError", "ValueError"]
idempotency: "event identity is supplied by immutable event_id; consumers MUST NOT mutate the event"
timeout: "not applicable to immutable value construction"
rate_limit: "not applicable to immutable value construction"
provenance: "provider, symbol, event_id, event_time, received_at"
tests: ["tests/unit/test_market_data_event.py"]
status: "ACTIVE"
```

The remaining baseline contracts are registry declarations only until their typed implementation and contract tests are present:

- `ingestion_provider_boundary`: NOT VERIFIED
- `provenance_metadata`: NOT VERIFIED
- `temporal_event_boundary`: NOT VERIFIED
- `validation_result`: NOT VERIFIED

These baseline IDs establish the registry namespace. Implementations MUST bind each ID to its actual typed contract before the corresponding behavior is released. An unbound contract is NOT VERIFIED.
