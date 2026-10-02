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
| backtest_confirmation_replay_boundary | backtest | ACTIVE | G03_UNIT_CONTRACT |
| strategy_evaluation_boundary | shared | ACTIVE | G03_UNIT_CONTRACT |
| decision_evaluation_boundary | shared | ACTIVE | G03_UNIT_CONTRACT |
| risk_evaluation_boundary | risk | ACTIVE | G03_UNIT_CONTRACT |
| cost_evaluation_boundary | cost | ACTIVE | G03_UNIT_CONTRACT |
| liquidity_evaluation_boundary | liquidity | ACTIVE | G03_UNIT_CONTRACT |
| pretrade_safety_boundary | risk | ACTIVE | G03_UNIT_CONTRACT |
| decision_audit_boundary | decision | ACTIVE | G03_UNIT_CONTRACT |
| opportunity_ranking_boundary | shared | ACTIVE | G03_UNIT_CONTRACT |
| opportunity_selection_boundary | shared | ACTIVE | G03_UNIT_CONTRACT |
| edge_evaluation_boundary | shared | ACTIVE | G03_UNIT_CONTRACT |
| performance_metrics_boundary | shared | ACTIVE | G03_UNIT_CONTRACT |
| market_structure_boundary | shared | ACTIVE | G03_UNIT_CONTRACT |
| backtest_market_structure_replay_boundary | backtest | ACTIVE | G03_UNIT_CONTRACT |
| mtf_structure_alignment_boundary | shared | ACTIVE | G03_UNIT_CONTRACT |
| backtest_mtf_structure_replay_boundary | backtest | ACTIVE | G03_UNIT_CONTRACT |
| setup_evaluation_boundary | shared | ACTIVE | G03_UNIT_CONTRACT |
| backtest_setup_replay_boundary | backtest | ACTIVE | G03_UNIT_CONTRACT |
| backtest_strategy_replay_boundary | backtest | ACTIVE | G03_UNIT_CONTRACT |
| backtest_performance_analysis_replay_boundary | backtest | ACTIVE | G03_UNIT_CONTRACT |

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

The v1 executable methodology is `decision.decision_engine.DeterministicDecisionEngine`: it maps normalized signal and descriptive confidence inputs to `BUY`, `SELL`, or `WAIT` using fixed ±0.5 thresholds. The confidence value is carried as a bounded descriptive score and is not a calibrated probability. The engine owns no cost, liquidity, risk sizing, persistence, or execution semantics.

`risk.decision_risk_gate.DecisionRiskGate` is the explicit Decision-to-Risk handoff: `BUY` maps to +1.0 signal, `SELL` to -1.0, and `WAIT` to 0.0 before the existing deterministic Risk gates are applied. It preserves the Decision event time and uses the Decision `decision_id` as the Risk source-event identity. It does not alter decision semantics or introduce cost, liquidity, persistence, or execution behavior.

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
allowed_consumers: ["strategy", "backtest", "evidence"]
forbidden_consumers: ["ingestion.providers", "persistence", "risk", "decision"]
signature: "composition.composer.SignalComposer/composition.composer.CompositionRequest/composition.composer.CompositionOutput"
async_mode: "SYNC"
error_taxonomy: ["ValueError"]
idempotency: "immutable value-object boundary; no external side effects"
timeout: "caller-owned CPU budget"
rate_limit: "N/A — no external I/O"
provenance: "source_event_id, event_time, received_at"
tests: ["tests/contract/test_composition_contract.py", "tests/unit/test_deterministic_mean_composer.py"]
status: "ACTIVE"
```

The v1 executable methodology is `composition.deterministic_mean.DeterministicEqualWeightMeanComposer`: it consumes normalized evidence in [-1.0, 1.0] and returns the equal-weight arithmetic mean. The methodology is deterministic and market-agnostic across Crypto, Forex, and Gold; it does not own cost, liquidity, risk, decision, or trading semantics.

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

Confirmation is an analytical boundary only. The v1 executable methodology is `composition.deterministic_confirmation.DeterministicMajorityConfirmation`: it ignores zero-valued directions, requires a minimum number of active signals, and emits the winning directional share as a descriptive score. Confirmation is true only when the absolute score reaches the configured agreement threshold. The methodology is deterministic and market-agnostic across Crypto, Forex, and Gold; it does not generate signals or finalize trading decisions.

### setup_evaluation_boundary

```yaml
contract_id: "setup_evaluation_boundary"
version: "1.0.0"
owner_layer: "shared"
allowed_consumers: ["analysis", "composition", "strategy", "backtest", "evidence"]
forbidden_consumers: ["ingestion.providers", "persistence", "risk", "decision", "output"]
signature: "shared.interfaces.setup.Setup/shared.interfaces.setup.SetupRequest/shared.interfaces.setup.SetupOutput"
async_mode: "SYNC"
error_taxonomy: ["ValueError"]
idempotency: "immutable value-object boundary; no external side effects"
timeout: "caller-owned CPU budget"
rate_limit: "N/A — no external I/O"
provenance: "source_event_id, event_time, received_at"
tests: ["tests/contract/test_setup_contract.py"]
status: "ACTIVE"
```

Setup is a descriptive analytical boundary only. It produces a normalized directional setup observation; it does not finalize confirmation, cost, liquidity, risk, trading action, or decision semantics.\n\nThe v1 executable methodology is `analysis.setup.deterministic_directional_setup.DeterministicDirectionalSetup`: it classifies the arithmetic mean of normalized evidence at ±0.5 thresholds and uses absolute aggregate magnitude as descriptive strength. The rule is deterministic and not a profitability or calibration claim.

### backtest_setup_replay_boundary

```yaml
contract_id: "backtest_setup_replay_boundary"
version: "1.0.0"
owner_layer: "backtest"
allowed_consumers: ["backtest", "evidence", "output"]
forbidden_consumers: ["ingestion.providers", "strategy", "risk", "decision"]
signature: "backtest.setup_replay.SetupReplay/backtest.setup_replay.SetupReplayOutput"
async_mode: "SYNC"
error_taxonomy: ["ValueError", "TypeError"]
idempotency: "immutable value-object output; no external side effects"
timeout: "caller-owned CPU budget"
rate_limit: "N/A — no external I/O"
provenance: "event_time, source_event_id from request; SetupOutput v1 does not expose source_event_id"
tests: ["tests/unit/test_setup_replay.py"]
status: "ACTIVE"
```

Setup replay is a point-in-time analytical replay consumer. It preserves request ordering, delegates each request once, validates output event-time alignment, and introduces no provider, persistence, cost, liquidity, risk, confirmation, decision, or trading semantics.

### backtest_strategy_replay_boundary

```yaml
contract_id: "backtest_strategy_replay_boundary"
version: "1.0.0"
owner_layer: "backtest"
allowed_consumers: ["backtest", "evidence", "output"]
forbidden_consumers: ["ingestion.providers", "persistence", "cost", "liquidity", "risk", "decision"]
signature: "backtest.strategy_replay.StrategyReplay/backtest.strategy_replay.StrategyReplayOutput"
async_mode: "SYNC"
error_taxonomy: ["ValueError", "TypeError"]
idempotency: "immutable value-object output; no external side effects"
timeout: "caller-owned CPU budget"
rate_limit: "N/A — no external I/O"
provenance: "source_event_id, event_time, received_at from StrategyRequest; strategy_id and event_time from StrategyOutput"
tests: ["tests/unit/test_strategy_replay.py", "tests/unit/test_replay_engine.py"]
status: "ACTIVE"
```

Strategy replay is a point-in-time analytical replay consumer. It delegates each ordered StrategyRequest exactly once, validates output event-time alignment, and introduces no portfolio accounting, performance metrics, cost, liquidity, risk, decision, or trading-execution semantics.

### strategy_evaluation_boundary

```yaml
contract_id: "strategy_evaluation_boundary"
version: "1.0.0"
owner_layer: "shared"
signature: "shared.interfaces.strategy.Strategy/shared.interfaces.strategy.StrategyRequest/shared.interfaces.strategy.StrategyOutput"
async_mode: "SYNC"
status: "ACTIVE"
```

The v1 strategy consumer is `strategy.trend.donchian.DonchianStrategy`, a deterministic close-confirmed long/flat breakout sensor that computes channels from prior bars only. The executable backtest consumer is `backtest.donchian_engine.DonchianBacktestEngine`, which applies a confirmed position from the next bar and constructs an immutable point-in-time EquityCurve. This slice does not estimate transaction costs, liquidity, risk, execution, or profitability.

### opportunity_ranking_boundary

```yaml
contract_id: "opportunity_ranking_boundary"
version: "1.1.0"
owner_layer: "shared"
allowed_consumers: ["analysis", "backtest", "evidence", "output"]
forbidden_consumers: ["ingestion.providers", "cost", "liquidity", "risk", "execution"]
signature: "analysis.opportunity_ranker.DeterministicOpportunityRanker/shared.contracts.opportunity_ranking.OpportunityRankingRequest/shared.contracts.opportunity_ranking.OpportunityRankingOutput"
async_mode: "SYNC"
error_taxonomy: ["ValueError"]
idempotency: "immutable value-object boundary; no external side effects"
timeout: "caller-owned CPU budget"
rate_limit: "N/A — no external I/O"
provenance: "source_safety_id, source_edge_id, event_time"
tests: ["tests/contract/test_opportunity_ranking.py", "tests/unit/test_opportunity_ranker.py"]
status: "ACTIVE"
```

The v1 executable methodology is `analysis.opportunity_ranker.DeterministicOpportunityRanker`: after the existing pre-trade safety gate has approved an action, it produces a deterministic descriptive ranking score as the equal-weight mean of decision confidence and a bounded edge score. The score is an ordering signal, not a probability, profitability claim, or approval mechanism. Ineligible safety outputs remain `NO_TRADE` and receive rank score `0.0`. The methodology is market-agnostic across Crypto, Forex, and Gold.

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

The v1 executable consumer path is `backtest.donchian_evaluation.DonchianPerformanceEvaluator`: it delegates the strategy-aware Donchian equity-curve construction and then delegates terminal metrics to the canonical performance-analysis replay boundary. It does not alter metric semantics or introduce cost, liquidity, risk, decision, execution, or profitability claims.

### liquidity_evaluation_boundary

```yaml
contract_id: "liquidity_evaluation_boundary"
version: "1.0.0"
owner_layer: "liquidity"
allowed_consumers: ["liquidity", "cost", "risk", "decision", "backtest", "evidence"]
forbidden_consumers: ["ingestion.providers", "persistence", "execution"]
signature: "shared.contracts.liquidity.LiquidityRequest/shared.contracts.liquidity.LiquidityOutput"
async_mode: "SYNC"
error_taxonomy: ["ValueError"]
idempotency: "immutable value-object boundary; no external side effects"
timeout: "caller-owned CPU budget"
rate_limit: "N/A — no external I/O"
provenance: "source_event_id, event_time, received_at"
tests: ["tests/unit/test_liquidity_engine.py"]
status: "ACTIVE"
```

The v1 executable methodology is `liquidity.liquidity_engine.DeterministicLiquidityEngine`: it accepts externally supplied normalized depth and participation observations and approves only when available depth meets required depth and requested participation stays at or below the supplied participation ceiling. It is a deterministic liquidity gate, not a liquidity estimator; market-data acquisition and depth estimation remain outside this boundary. The methodology is market-agnostic across Crypto, Forex, and Gold and owns no cost, risk sizing, decision generation, persistence, or execution semantics.

### cost_evaluation_boundary

```yaml
contract_id: "cost_evaluation_boundary"
version: "1.0.0"
owner_layer: "cost"
allowed_consumers: ["cost", "risk", "decision", "backtest", "evidence"]
forbidden_consumers: ["ingestion.providers", "persistence", "execution"]
signature: "shared.contracts.cost.CostRequest/shared.contracts.cost.CostOutput"
async_mode: "SYNC"
error_taxonomy: ["ValueError"]
idempotency: "immutable value-object boundary; no external side effects"
timeout: "caller-owned CPU budget"
rate_limit: "N/A — no external I/O"
provenance: "source_event_id, event_time, received_at"
tests: ["tests/unit/test_cost_engine.py"]
status: "ACTIVE"
```

The v1 executable methodology is `cost.cost_engine.DeterministicCostEngine`: it aggregates supplied spread, slippage, and fee fractions and approves the total only when it is at or below the supplied maximum cost fraction. It is a deterministic cost gate, not a market-cost estimator; missing or external cost observations remain outside this boundary. The methodology is market-agnostic across Crypto, Forex, and Gold and owns no liquidity, risk sizing, decision generation, persistence, or execution semantics.

### risk_evaluation_boundary

```yaml
contract_id: "risk_evaluation_boundary"
version: "1.0.0"
owner_layer: "risk"
signature: "risk.risk_engine.RiskRequest/risk.risk_engine.RiskOutput"
async_mode: "SYNC"
status: "ACTIVE"
```

The v1 executable methodology is `risk.risk_engine.DeterministicRiskEngine`: it requires normalized signal, descriptive confidence, requested exposure, and maximum exposure. Approval requires absolute signal and confidence at or above 0.5 and requested exposure no greater than the supplied cap. Approved exposure is exactly the requested bounded fraction; rejected requests produce zero exposure. The methodology is deterministic and market-agnostic across Crypto, Forex, and Gold. It does not estimate cost/liquidity, generate decisions, persist state, or execute trades.


### pretrade_safety_boundary

```yaml
contract_id: "pretrade_safety_boundary"
version: "1.0.0"
owner_layer: "risk"
allowed_consumers: ["risk", "decision", "backtest", "output", "evidence"]
forbidden_consumers: ["ingestion.providers", "persistence", "execution"]
signature: "shared.contracts.pretrade_safety.PreTradeSafetyOutput"
async_mode: "SYNC"
error_taxonomy: ["ValueError"]
idempotency: "immutable value-object boundary; no external side effects"
timeout: "caller-owned CPU budget"
rate_limit: "N/A — no external I/O"
provenance: "decision_id, cost_id, liquidity_id, risk_id, event_time"
tests: ["tests/unit/test_pretrade_safety_gate.py"]
status: "ACTIVE"
```

The v1 executable methodology is `risk.pretrade_safety_gate.PreTradeSafetyGate`: it aggregates already-evaluated Decision, Cost, Liquidity, and Risk outputs. Any failed safety gate or a Decision of WAIT yields `NO_TRADE` with explicit machine-readable reasons; only BUY/SELL with all gates approved can pass. This boundary does not estimate cost or liquidity, calculate risk, submit orders, persist state, or claim profitability. It is market-agnostic across Crypto, Forex, and Gold.

### decision_audit_boundary

```yaml
contract_id: "decision_audit_boundary"
version: "1.1.0"
owner_layer: "decision"
allowed_consumers: ["decision", "backtest", "output", "evidence"]
forbidden_consumers: ["ingestion.providers", "persistence", "execution"]
signature: "shared.contracts.decision_audit.DecisionAuditRecord"
async_mode: "SYNC"
error_taxonomy: ["ValueError"]
idempotency: "immutable value-object boundary; no external side effects"
timeout: "caller-owned CPU budget"
rate_limit: "N/A — no external I/O"
provenance: "decision_id, cost_id, liquidity_id, risk_id, safety_id, event_time"
tests: ["tests/unit/test_decision_audit.py"]
status: "ACTIVE"
```

The v1 executable methodology is `decision.decision_audit.DecisionAuditRecorder`: it creates deterministic reconstruction metadata from the canonical Decision, Cost, Liquidity, Risk, and PreTradeSafety boundary IDs. It does not persist records, execute trades, recalculate upstream metrics, or make a new trading decision. The record is market-agnostic across Crypto, Forex, and Gold.

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

### mtf_structure_alignment_boundary

```yaml
contract_id: "mtf_structure_alignment_boundary"
version: "1.0.0"
owner_layer: "shared"
allowed_consumers: ["analysis", "backtest", "evidence"]
forbidden_consumers: ["ingestion.providers", "persistence", "risk", "decision"]
signature: "shared.contracts.mtf_structure.MtfStructureEvaluator/shared.contracts.mtf_structure.MtfStructureInput/shared.contracts.mtf_structure.MtfStructureRequest/shared.contracts.mtf_structure.MtfStructureObservation/shared.contracts.mtf_structure.MtfStructureOutput"
async_mode: "SYNC"
error_taxonomy: ["ValueError"]
idempotency: "immutable value-object boundary; no external side effects"
timeout: "caller-owned CPU budget"
rate_limit: "N/A — no external I/O"
provenance: "source_event_id, event_time, received_at"
tests: ["tests/contract/test_mtf_structure_contract.py"]
status: "ACTIVE"
```

### backtest_confirmation_replay_boundary

```yaml
contract_id: "backtest_confirmation_replay_boundary"
version: "1.0.0"
owner_layer: "backtest"
allowed_consumers: ["backtest", "evidence", "output"]
forbidden_consumers: ["ingestion.providers", "strategy", "risk", "decision"]
signature: "backtest.confirmation_replay.ConfirmationReplay/backtest.confirmation_replay.ConfirmationReplayOutput"
async_mode: "SYNC"
error_taxonomy: ["ValueError", "TypeError"]
idempotency: "immutable value-object output; no external side effects"
timeout: "caller-owned CPU budget"
rate_limit: "N/A — no external I/O"
provenance: "event_time from request; confirmation outputs preserve point-in-time alignment"
tests: ["tests/unit/test_confirmation_replay.py", "tests/unit/test_replay_engine.py"]
status: "ACTIVE"
```

Confirmation replay is a point-in-time analytical replay boundary. It delegates methodology execution, preserves strict event-time ordering, validates output alignment, and owns no provider, persistence, cost, liquidity, risk, decision, or trading semantics.

### backtest_mtf_structure_replay_boundary

```yaml
contract_id: "backtest_mtf_structure_replay_boundary"
version: "1.0.0"
owner_layer: "backtest"
allowed_consumers: ["backtest", "evidence", "output"]
forbidden_consumers: ["ingestion.providers", "strategy", "risk", "decision"]
signature: "backtest.mtf_structure_replay.MtfStructureReplay/backtest.mtf_structure_replay.MtfStructureReplayOutput"
async_mode: "SYNC"
error_taxonomy: ["ValueError", "TypeError"]
idempotency: "immutable value-object output; no external side effects"
timeout: "caller-owned CPU budget"
rate_limit: "N/A — no external I/O"
provenance: "source_event_id, event_time, received_at"
tests: ["tests/unit/test_mtf_structure_replay.py"]
status: "ACTIVE"
```

Multi-timeframe structure is a descriptive analytical boundary. It aligns already-evaluated point-in-time structure observations; it does not detect swings, consume provider data, or finalize trading decisions.


### backtest_performance_analysis_replay_boundary

```yaml
contract_id: "backtest_performance_analysis_replay_boundary"
version: "1.0.0"
owner_layer: "backtest"
allowed_consumers: ["backtest", "evidence", "output"]
forbidden_consumers: ["ingestion.providers", "persistence", "cost", "liquidity", "risk", "decision"]
signature: "backtest.performance_replay.PerformanceAnalysisReplay/backtest.performance_replay.PerformanceAnalysisReplayOutput"
async_mode: "SYNC"
error_taxonomy: ["TypeError", "ValueError"]
idempotency: "immutable value-object output; no external side effects"
timeout: "caller-owned CPU budget"
rate_limit: "N/A — no external I/O"
provenance: "EquityCurve timestamps/equity/drawdown; PerformanceMetricsData fields"
tests: ["tests/unit/test_performance_replay.py"]
status: "ACTIVE"
```

Performance analysis replay is a point-in-time analytical boundary over an already-produced EquityCurve. It delegates deterministic terminal metric calculation and introduces no portfolio construction, market-data I/O, cost, liquidity, risk, decision, or trading-execution semantics.
### opportunity_selection_boundary

```yaml
contract_id: "opportunity_selection_boundary"
version: "1.1.0"
owner_layer: "shared"
allowed_consumers: ["analysis", "backtest", "evidence", "output"]
forbidden_consumers: ["ingestion.providers", "cost", "liquidity", "risk", "execution"]
signature: "shared.contracts.opportunity_selection.OpportunitySelectionOutput"
async_mode: "SYNC"
error_taxonomy: ["ValueError"]
idempotency: "immutable value-object boundary; no external side effects"
timeout: "caller-owned CPU budget"
rate_limit: "N/A — no external I/O"
provenance: "source ranking_id, source_safety_id, event_time"
tests: ["tests/unit/test_opportunity_selector.py", "tests/integration/test_opportunity_selection_pipeline.py"]
status: "ACTIVE"
```

The v1 executable methodology is `analysis.opportunity_selector.OpportunitySelector`: it filters already-ranked eligible opportunities, preserves canonical rank scores, applies deterministic descending ordering with a bounded selection limit, and emits a deterministic `selection_id` derived from the selected ranking IDs. It does not recompute ranking, safety, cost, liquidity, risk, execution, or profitability. The boundary is market-agnostic across Crypto, Forex, and Gold.


### edge_evaluation_boundary

```yaml
contract_id: "edge_evaluation_boundary"
version: "1.0.0"
owner_layer: "shared"
allowed_consumers: ["analysis", "backtest", "evidence", "output"]
forbidden_consumers: ["ingestion.providers", "execution", "persistence"]
signature: "shared.contracts.edge_evaluation.EdgeEvaluationRequest/shared.contracts.edge_evaluation.EdgeEvaluationOutput"
async_mode: "SYNC"
error_taxonomy: ["ValueError"]
idempotency: "immutable value-object boundary; no external side effects"
timeout: "caller-owned CPU budget"
rate_limit: "N/A — no external I/O"
provenance: "source setup_id, source confirmation_id, event_time"
tests: ["tests/contract/test_edge_evaluation_contract.py", "tests/unit/test_edge_evaluator.py"]
status: "ACTIVE"
```

The v1 methodology computes a descriptive normalized edge score as the equal-weight mean of setup quality, confirmation strength, regime alignment, liquidity quality, and cost efficiency. Inputs must already be normalized to [0, 1]. The score is an ordering feature only; it is not a probability, expected return, or profitability guarantee. The boundary is market-agnostic across Crypto, Forex, and Gold. The composition adapter `composition.edge_evaluation_pipeline.EdgeEvaluationPipeline` consumes canonical `SetupOutput` and confirmed `ConfirmationOutput` and preserves their point-in-time identities. The regime adapter `composition.regime_edge_pipeline.RegimeEdgeEvaluationPipeline` consumes canonical `RegimeAnalysisOutput`, validates point-in-time alignment, and derives only a normalized descriptive regime-alignment value from setup direction plus regime label/confidence before delegating to the existing edge methodology. The cost/liquidity adapter `composition.cost_liquidity_edge_pipeline.CostLiquidityEdgeEvaluationPipeline` requires approved canonical `CostOutput` and `LiquidityOutput`, validates their point-in-time alignment, and passes only explicit normalized descriptive cost-efficiency and liquidity-quality values downstream. The composed opportunity adapter `composition.opportunity_chain_pipeline.ComposedOpportunityChainPipeline` delegates the canonical edge result to the existing analysis-layer opportunity ranking/selection chain without recalculation. These adapters do not estimate upstream observations or introduce risk, decision, execution, or profitability semantics.
