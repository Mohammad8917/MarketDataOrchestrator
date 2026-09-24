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
| equity_curve | shared | ACTIVE | G03_UNIT_CONTRACT |

## Typed contract bindings

### market_data_event

```yaml
contract_id: "market_data_event"
version: "1.0.0"
owner_layer: "domain"
allowed_consumers: ["ingestion", "analysis", "backtest", "validation", "persistence"]
forbidden_consumers: ["app", "core", "strategy", "decision", "risk", "output"]
signature: "domain.market_data_event.MarketDataEvent"
consumer: "persistence.market_data_store.MarketDataStore"
async_mode: "SYNC"
error_taxonomy: ["TypeError", "ValueError"]
idempotency: "event_id is deterministic UUID5 over canonical semantic fields; persistence treats event_id as the unique storage key"
timeout: "not applicable to local SQLite value persistence"
rate_limit: "not applicable to local SQLite persistence"
provenance: "provider, symbol, event_id, event_time, received_at"
tests: ["tests/unit/test_market_data_event.py", "tests/contract/test_market_data_store.py"]
status: "ACTIVE"
```


### equity_curve

```yaml
contract_id: "equity_curve"
version: "1.0.0"
owner_layer: "shared"
allowed_consumers: ["backtest", "feedback", "output", "validation"]
forbidden_consumers: ["app", "core", "config", "ingestion", "persistence", "strategy", "decision", "risk"]
signature: "shared.contracts.equity_curve.EquityCurve"
consumer: "backtest.engine.BacktestEngine"
async_mode: "SYNC"
error_taxonomy: ["TypeError", "ValueError"]
idempotency: "not applicable to an output protocol"
timeout: "not applicable to interface-only contract"
rate_limit: "not applicable to local backtest output"
provenance: "timestamps, equity, drawdown"
tests: ["tests/contract/test_backtest_interfaces.py"]
status: "ACTIVE"
```

The `equity_curve` record is an interface-only terminal output contract. It is NOT VERIFIED
until a legitimate producer, applicable contract tests, CI evidence, and the required
evidence fingerprint exist.

The `market_data_event` contract has an executable persistence consumer. Verification still requires successful execution of the applicable CI gates and evidence capture; registry binding alone is not PASS.

The remaining baseline contracts are registry declarations only until their typed implementation, legitimate consumer relationship, and contract tests are present:

- `ingestion_provider_boundary`: NOT VERIFIED
- `provenance_metadata`: NOT VERIFIED
- `temporal_event_boundary`: NOT VERIFIED
- `validation_result`: NOT VERIFIED

These baseline IDs establish the registry namespace. Implementations MUST bind each ID to their actual typed contract before the corresponding behavior is released. An unbound contract is NOT VERIFIED.
