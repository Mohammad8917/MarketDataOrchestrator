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
signature: "ingestion.interfaces.market_provider.MarketDataProvider/ingestion.interfaces.market_provider.MarketEvent"
async_mode: "ASYNC"
error_taxonomy: ["provider-isolated exceptions", "TimeoutError", "CancelledError"]
idempotency: "fetch is read-only; event identity is source_event_id"
timeout: "caller-owned bounded timeout"
rate_limit: "provider-owned policy"
provenance: "source_event_id, source, symbol, event_time, received_at, payload_digest"
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
signature: "ingestion.interfaces.market_provider.MarketEvent"
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
```

### risk_evaluation_boundary

```yaml
contract_id: "risk_evaluation_boundary"
version: "1.0.0"
owner_layer: "risk"
allowed_consumers: ["output", "persistence", "backtest"]
forbidden_consumers: ["ingestion.providers", "domain_adapters", "strategy"]
signature: "risk.risk_engine.RiskRequest/risk.risk_engine.RiskOutput"
async_mode: "SYNC"
error_taxonomy: ["ValueError"]
idempotency: "immutable value-object boundary; no external side effects"
timeout: "caller-owned CPU budget"
rate_limit: "N/A — no external I/O"
provenance: "source_event_id, event_time, received_at"
tests: ["tests/contract/test_risk_contract.py"]
status: "ACTIVE"
```


### temporal_event_boundary

```yaml
contract_id: "temporal_event_boundary"
version: "1.0.0"
owner_layer: "validation"
allowed_consumers: ["ingestion", "analysis", "regime", "composition", "strategy", "decision", "risk", "persistence"]
forbidden_consumers: ["provider business logic ownership"]
signature: "validation.temporal_validator.validate_event_boundary/validation.temporal_validator.assess_clock_skew/validation.temporal_validator.validate_elapsed_duration"
async_mode: "SYNC"
error_taxonomy: ["ValueError"]
idempotency: "pure validation"
timeout: "N/A — no external I/O"
rate_limit: "N/A — no external I/O"
provenance: "event_time, received_at, provider_time, local_time"
tests: ["tests/validation/test_temporal_validator.py"]
status: "ACTIVE"
```

### provenance_metadata

```yaml
contract_id: "provenance_metadata"
version: "1.0.0"
owner_layer: "shared"
allowed_consumers: ["evidence", "domain", "analysis", "regime", "composition", "strategy", "backtest", "decision", "risk"]
forbidden_consumers: ["provider implementation details", "persistence mutation"]
signature: "shared.models.evidence.ProvenanceMetadata"
async_mode: "SYNC"
error_taxonomy: ["ValueError"]
idempotency: "immutable value object; no external side effects"
timeout: "N/A — pure validation"
rate_limit: "N/A — no external I/O"
provenance: "source_event_id, source, observed_at, received_at, content_digest"
tests: ["tests/contract/test_provenance_contract.py", "tests/architecture/test_provenance_single_source.py"]
status: "ACTIVE"
```

The provenance contract is the canonical traceability payload. It separates source observation time from receipt time, requires UTC-aware timestamps and a content digest, and performs no I/O. Concrete evidence algorithms remain owned by the evidence subsystem and must bind to this contract before release.

### indicator_execution_boundary

```yaml
contract_id: "indicator_execution_boundary"
version: "1.0.0"
owner_layer: "indicators"
allowed_consumers: ["analysis", "regime", "composition", "strategy"]
forbidden_consumers: ["ingestion.providers", "domain_adapters", "decision", "risk"]
signature: "indicators.core.base.Indicator/indicators.core.base.IndicatorRequest/indicators.core.base.IndicatorOutput"
async_mode: "SYNC"
error_taxonomy: ["ValueError", "contract-defined calculation errors"]
idempotency: "same request produces the same output; no external side effects"
timeout: "caller-owned CPU budget; no external I/O"
rate_limit: "N/A — pure in-memory computation"
provenance: "source_event_id, event_time, received_at"
tests: ["tests/contract/test_indicator_contract.py", "tests/architecture/test_indicator_single_source.py"]
status: "ACTIVE"
```

The indicator contract is protocol-only: concrete algorithms remain separately owned by their indicator files and MUST implement this canonical protocol. It does not authorize provider I/O or cross-layer state ownership.

#### SMA concrete semantics

The `sma` implementation is a concrete binding to `indicator_execution_boundary`, not a separate cross-layer contract.

- Input: ordered `close` series from `IndicatorRequest`; the final `period` values form the calculation window.
- `period <= 0`: reject with `ValueError`.
- Empty series: reject with `ValueError`.
- `period > len(close)`: reject with `ValueError`.
- Non-numeric or boolean values: reject with `ValueError`.
- NaN or positive/negative infinity: reject with `ValueError`.
- Non-finite result caused by floating-point overflow: reject with `ValueError`.
- Constant finite values: return that same value.
- `period == 1`: return the input value.
- No provider I/O, timeframe inference, persistence, or strategy dependency is permitted.

The final-window reference example `[1,2,3,4,5]` with period `3` yields `4.0` under the conventional SMA definition. This is a fixed reference-value test, not an implementation-derived oracle.


### regime_classification_boundary

```yaml
contract_id: "regime_classification_boundary"
version: "1.0.0"
owner_layer: "regime"
allowed_consumers: ["analysis", "composition", "strategy"]
forbidden_consumers: ["ingestion.providers", "domain_adapters", "decision", "risk"]
signature: "regime.classification.regime_classifier.RegimeClassifier/regime.classification.regime_classifier.RegimeRequest/regime.classification.regime_classifier.RegimeOutput"
async_mode: "SYNC"
error_taxonomy: ["ValueError", "contract-defined classification errors"]
idempotency: "same request produces the same classification; no external side effects"
timeout: "caller-owned CPU budget; no external I/O"
rate_limit: "N/A — pure in-memory classification"
provenance: "source_event_id, event_time, received_at"
tests: ["tests/contract/test_regime_contract.py", "tests/architecture/test_regime_top_level.py"]
status: "ACTIVE"
```

The regime contract is the canonical classification boundary. Concrete detectors, classifiers, transition logic, and history components remain separately owned and MUST bind to this protocol before corresponding behavior is released. The contract does not permit look-ahead data, provider I/O, persistence mutation, decision finalization, or risk ownership.

### signal_composition_boundary

```yaml
contract_id: "signal_composition_boundary"
version: "1.0.0"
owner_layer: "composition"
allowed_consumers: ["strategy"]
forbidden_consumers: ["ingestion.providers", "domain_adapters", "decision", "risk"]
signature: "composition.composer.SignalComposer/composition.composer.CompositionRequest/composition.composer.CompositionOutput"
async_mode: "SYNC"
error_taxonomy: ["ValueError", "contract-defined composition errors"]
idempotency: "same request produces the same composition; no external side effects"
timeout: "caller-owned CPU budget; no external I/O"
rate_limit: "N/A — pure in-memory composition"
provenance: "source_event_id, event_time, received_at"
tests: ["tests/contract/test_composition_contract.py", "tests/architecture/test_composition_single_source.py"]
status: "ACTIVE"
```

The composition contract is the canonical boundary for combining upstream analytical signals. Concrete combiners, confirmation logic, correlation logic, divergence logic, and presets remain separately owned and MUST bind to this protocol before corresponding behavior is released. The contract does not permit provider I/O, persistence mutation, decision finalization, or risk ownership.

### strategy_evaluation_boundary

```yaml
contract_id: "strategy_evaluation_boundary"
version: "1.0.0"
owner_layer: "shared"
allowed_consumers: ["strategy", "backtest"]
forbidden_consumers: ["ingestion.providers", "domain_adapters", "decision", "risk"]
signature: "shared.interfaces.strategy.Strategy/shared.interfaces.strategy.StrategyRequest/shared.interfaces.strategy.StrategyOutput"
async_mode: "SYNC"
error_taxonomy: ["ValueError", "contract-defined strategy errors"]
idempotency: "same request produces the same evaluation; no external side effects"
timeout: "caller-owned CPU budget; no external I/O"
rate_limit: "N/A — pure in-memory evaluation"
provenance: "source_event_id, event_time, received_at"
tests: ["tests/contract/test_strategy_contract.py", "tests/architecture/test_strategy_single_source.py"]
status: "ACTIVE"
```

The strategy contract is the canonical evaluation boundary. Concrete definitions, selectors, execution logic, and evaluators remain separately owned and MUST bind to this protocol before corresponding behavior is released. It does not permit provider I/O, persistence mutation, decision finalization, or risk ownership.

These baseline IDs establish the registry namespace. Implementations MUST bind each ID to its actual typed contract before the corresponding behavior is released. An unbound contract is NOT VERIFIED.
