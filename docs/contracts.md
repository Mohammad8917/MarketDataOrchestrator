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
| regime_analysis_boundary | analysis | ACTIVE | G03_UNIT_CONTRACT |
| backtest_regime_analysis_boundary | backtest | ACTIVE | G03_UNIT_CONTRACT |
| regime_uncertainty_boundary | regime | ACTIVE | G03_UNIT_CONTRACT |
| volatility_state_boundary | volatility | ACTIVE | G03_UNIT_CONTRACT |
| signal_composition_boundary | composition | ACTIVE | G03_UNIT_CONTRACT |
| signal_confirmation_boundary | composition | ACTIVE | G03_UNIT_CONTRACT |
| backtest_composition_replay_boundary | backtest | ACTIVE | G03_UNIT_CONTRACT |
| strategy_evaluation_boundary | shared | ACTIVE | G03_UNIT_CONTRACT |
| decision_evaluation_boundary | shared | ACTIVE | G03_UNIT_CONTRACT |
| risk_evaluation_boundary | risk | ACTIVE | G03_UNIT_CONTRACT |
| performance_metrics_boundary | shared | ACTIVE | G03_UNIT_CONTRACT |
| market_structure_boundary | shared | ACTIVE | G03_UNIT_CONTRACT |

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
provenance: "event_id, provider, symbol, timeframe, event_time, received_at"
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

### provenance_metadata

```yaml
contract_id: "provenance_metadata"
version: "1.0.0"
owner_layer: "shared"
signature: "shared.models.evidence.ProvenanceMetadata"
async_mode: "SYNC"
status: "ACTIVE"
```

### temporal_event_boundary

```yaml
contract_id: "temporal_event_boundary"
version: "1.0.0"
owner_layer: "validation"
signature: "validation.temporal_validator.validate_event_boundary/validation.temporal_validator.assess_clock_skew/validation.temporal_validator.validate_elapsed_duration"
async_mode: "SYNC"
status: "ACTIVE"
```

### validation_result

No frozen typed value contract is currently bound to this registry ID; the boundary remains intentionally non-frozen pending an executable value contract.

### indicator_execution_boundary

```yaml
contract_id: "indicator_execution_boundary"
version: "1.0.0"
owner_layer: "indicators"
signature: "indicators.core.base.Indicator/indicators.core.base.IndicatorRequest/indicators.core.base.IndicatorOutput"
async_mode: "SYNC"
status: "ACTIVE"
```

### backtest_regime_analysis_boundary

```yaml
contract_id: "backtest_regime_analysis_boundary"
version: "1.0.0"
owner_layer: "backtest"
allowed_consumers: ["backtest", "evidence", "output"]
forbidden_consumers: ["ingestion.providers", "strategy", "risk", "decision"]
signature: "backtest.regime_analyzer.RegimeAnalysisReplay/backtest.regime_analyzer.RegimeAnalysisReplayOutput"
async_mode: "SYNC"
error_taxonomy: ["ValueError"]
idempotency: "immutable value-object output; no external side effects"
timeout: "caller-owned CPU budget"
rate_limit: "N/A — no external I/O"
provenance: "source_event_id, event_time, received_at"
tests: ["tests/contract/test_backtest_regime_analysis.py"]
status: "ACTIVE"
```

### regime_analysis_boundary

```yaml
contract_id: "regime_analysis_boundary"
version: "1.0.0"
owner_layer: "analysis"
allowed_consumers: ["backtest", "evidence", "output"]
forbidden_consumers: ["ingestion.providers", "strategy", "risk", "decision"]
signature: "analysis.regime_analysis.RegimeAnalysisEvaluator/analysis.regime_analysis.RegimeAnalysisOutput"
async_mode: "SYNC"
error_taxonomy: ["ValueError"]
idempotency: "immutable value-object boundary; no external side effects"
timeout: "caller-owned CPU budget"
rate_limit: "N/A — no external I/O"
provenance: "source_event_id, event_time, received_at"
tests: ["tests/contract/test_regime_analysis.py"]
status: "ACTIVE"
```

### regime_classification_boundary

```yaml
contract_id: "regime_classification_boundary"
version: "1.0.0"
owner_layer: "regime"
signature: "regime.classification.regime_classifier.RegimeClassifier/regime.classification.regime_classifier.RegimeRequest/regime.classification.regime_classifier.RegimeOutput"
async_mode: "SYNC"
status: "ACTIVE"
```

### regime_uncertainty_boundary

```yaml
contract_id: "regime_uncertainty_boundary"
version: "1.0.0"
owner_layer: "regime"
allowed_consumers: ["regime", "analysis", "backtest", "evidence"]
forbidden_consumers: ["ingestion.providers", "strategy", "risk", "decision"]
signature: "regime.uncertainty.regime_uncertainty.RegimeUncertaintyEvaluator/regime.uncertainty.regime_uncertainty.RegimeUncertaintyRequest/regime.uncertainty.regime_uncertainty.RegimeUncertaintyOutput"
async_mode: "SYNC"
error_taxonomy: ["ValueError"]
idempotency: "immutable value-object boundary; no external side effects"
timeout: "caller-owned CPU budget"
rate_limit: "N/A — no external I/O"
provenance: "source_event_id, event_time, received_at"
tests: ["tests/contract/test_regime_uncertainty.py"]
status: "ACTIVE"
```

### volatility_state_boundary

```yaml
contract_id: "volatility_state_boundary"
version: "1.0.0"
owner_layer: "volatility"
allowed_consumers: ["analysis", "backtest", "evidence"]
forbidden_consumers: ["ingestion.providers", "strategy", "risk", "decision"]
signature: "volatility.state.volatility_state.VolatilityStateEvaluator/volatility.state.volatility_state.VolatilityStateRequest/volatility.state.volatility_state.VolatilityStateOutput"
async_mode: "SYNC"
error_taxonomy: ["ValueError"]
idempotency: "immutable value-object boundary; no external side effects"
timeout: "caller-owned CPU budget"
rate_limit: "N/A — no external I/O"
provenance: "source_event_id, event_time, received_at"
tests: ["tests/contract/test_volatility_state.py"]
status: "ACTIVE"
```

### signal_composition_boundary

```yaml
contract_id: "signal_composition_boundary"
version: "1.0.0"
owner_layer: "composition"
signature: "composition.composer.SignalComposer/composition.composer.CompositionRequest/composition.composer.CompositionOutput"
async_mode: "SYNC"
status: "ACTIVE"
```

### signal_confirmation_boundary

~~~~yaml
contract_id: "signal_confirmation_boundary"
version: "1.0.0"
owner_layer: "composition"
allowed_consumers: ["strategy", "analysis", "backtest", "evidence"]
forbidden_consumers: ["ingestion.providers", "persistence", "risk", "decision"]
signature: "composition.confirmation_contract.SignalConfirmation/composition.confirmation_contract.ConfirmationRequest/composition.confirmation_contract.ConfirmationOutput"
async_mode: "SYNC"
error_taxonomy: ["ValueError"]
idempotency: "immutable value-object boundary; no external side effects"
timeout: "caller-owned CPU budget"
rate_limit: "N/A — no external I/O"
provenance: "source_event_id, event_time, received_at"
tests: ["tests/contract/test_confirmation_contract.py"]
status: "ACTIVE"
~~~~

Confirmation is an analytical boundary only. The contract does not define a confirmation methodology, trading action, cost, liquidity, risk, or decision semantics.

### strategy_evaluation_boundary

```yaml
contract_id: "strategy_evaluation_boundary"
version: "1.0.0"
owner_layer: "shared"
signature: "shared.interfaces.strategy.Strategy/shared.interfaces.strategy.StrategyRequest/shared.interfaces.strategy.StrategyOutput"
async_mode: "SYNC"
status: "ACTIVE"
```

### performance_metrics_boundary

```yaml
contract_id: "performance_metrics_boundary"
version: "1.0.0"
owner_layer: "shared"
allowed_consumers: ["strategy", "backtest", "output"]
forbidden_consumers: ["ingestion.providers", "persistence"]
signature: "shared.contracts.performance_metrics.PerformanceMetrics/shared.contracts.performance_metrics.PerformanceMetricsData"
async_mode: "SYNC"
error_taxonomy: ["ValueError"]
idempotency: "immutable value-object boundary; no external side effects"
timeout: "caller-owned CPU budget"
rate_limit: "N/A — no external I/O"
provenance: "observations, initial_equity, final_equity, total_return, max_drawdown"
tests: ["tests/unit/test_performance_metrics_contract.py", "tests/unit/test_performance_metrics.py"]
status: "ACTIVE"
```

### risk_evaluation_boundary

```yaml
contract_id: "risk_evaluation_boundary"
version: "1.0.0"
owner_layer: "risk"
signature: "risk.risk_engine.RiskRequest/risk.risk_engine.RiskOutput"
async_mode: "SYNC"
status: "ACTIVE"
```


### market_structure_boundary

```yaml
contract_id: "market_structure_boundary"
version: "1.0.0"
owner_layer: "shared"
allowed_consumers: ["regime", "analysis", "backtest", "strategy", "evidence"]
forbidden_consumers: ["ingestion.providers", "persistence", "risk", "decision", "output"]
signature: "shared.contracts.market_structure.MarketStructureEvaluator/shared.contracts.market_structure.MarketStructureBar/shared.contracts.market_structure.MarketStructureRequest/shared.contracts.market_structure.StructurePoint/shared.contracts.market_structure.StructureEvent/shared.contracts.market_structure.StructureState/shared.contracts.market_structure.MarketStructureOutput"
async_mode: "SYNC"
error_taxonomy: ["ValueError", "TypeError"]
idempotency: "immutable value-object boundary; no external side effects"
timeout: "caller-owned CPU budget"
rate_limit: "N/A — no external I/O"
provenance: "source_event_id, event_time, received_at"
tests: ["tests/contract/test_market_structure_contract.py", "tests/contract/test_frozen_contracts.py"]
status: "ACTIVE"
```

Market Structure is a descriptive analytical boundary only. The contract defines the structural vocabulary (HH, HL, LH, LL; breakout, breakdown, structure_shift; range, expansion, compression) and point-in-time input/output semantics. Detection thresholds, swing methodology, confirmation rules, and trading actions are intentionally outside this contract and require a separate formal methodology before implementation.



### backtest_market_structure_replay_boundary

```yaml
contract_id: "backtest_market_structure_replay_boundary"
version: "1.0.0"
owner_layer: "backtest"
allowed_consumers: ["backtest", "evidence", "output"]
forbidden_consumers: ["ingestion.providers", "strategy", "risk", "decision"]
signature: "backtest.market_structure_replay.MarketStructureReplay/backtest.market_structure_replay.MarketStructureReplayOutput"
async_mode: "SYNC"
error_taxonomy: ["ValueError", "TypeError"]
idempotency: "immutable value-object output; no external side effects"
timeout: "caller-owned CPU budget"
rate_limit: "N/A — no external I/O"
provenance: "source_event_id, event_time, received_at"
tests: ["tests/unit/test_market_structure_replay.py"]
status: "ACTIVE"
```

### backtest_composition_replay_boundary

```yaml
contract_id: "backtest_composition_replay_boundary"
version: "1.0.0"
owner_layer: "backtest"
allowed_consumers: ["backtest", "evidence", "output"]
forbidden_consumers: ["ingestion.providers", "strategy", "risk", "decision"]
signature: "backtest.composition_replay.CompositionReplay/backtest.composition_replay.CompositionReplayOutput"
async_mode: "SYNC"
error_taxonomy: ["ValueError", "TypeError"]
idempotency: "immutable value-object output; no external side effects"
timeout: "caller-owned CPU budget"
rate_limit: "N/A — no external I/O"
provenance: "source_event_id, event_time, received_at"
tests: ["tests/unit/test_composition_replay.py"]
status: "ACTIVE"
```
