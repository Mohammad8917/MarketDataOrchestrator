# Consumer Matrix

Architecture Frozen v1.0 — contract producer/consumer inventory.

| Contract | Producer | Consumer(s) found in repository | Verification status |
|---|---|---|---|
| `market_data_event` | `domain.market_data_event.MarketDataEvent` | `persistence.market_data_store.MarketDataStore` | ACTIVE — CI evidence pending |
| `market_data_store` (component output) | `persistence.market_data_store.MarketDataStore.read_all()` | `backtest.engine.BacktestEngine.run()` typed input boundary | TYPE-CONSUMER-PLANNED — interface exists; no production implementation calls `read_all()` yet |
| `signal_composition_boundary` | `composition` | `backtest.composition_replay.CompositionReplay`, wired by `backtest.replay_engine.BacktestReplayEngine`; frozen output `backtest.composition_replay.CompositionReplayOutput` | ACTIVE — executable replay consumer and canonical Backtest integration |
| `market_structure_boundary` | `shared.contracts.market_structure` | `analysis.structure.market_structure.DeterministicMarketStructureEvaluator` → `backtest.market_structure_replay.MarketStructureReplay` → `backtest.replay_engine.BacktestReplayEngine`; frozen output `backtest.market_structure_replay.MarketStructureReplayOutput` | ACTIVE — executable methodology, replay consumer, and canonical Backtest integration |
| `signal_confirmation_boundary` | `composition` | `backtest.confirmation_replay.ConfirmationReplay`, wired by `backtest.replay_engine.BacktestReplayEngine` | ACTIVE — executable replay consumer and canonical Backtest integration |
| `ingestion_provider_boundary` | Not implemented | None found | NOT VERIFIED |
| `provenance_metadata` | Not implemented | None found | NOT VERIFIED |
| `temporal_event_boundary` | Ownership unresolved | None found | NOT VERIFIED |
| `validation_result` | Not implemented | None found | NOT VERIFIED |
| `equity_curve` | `backtest` production producer not implemented | `backtest.engine.BacktestEngine` typed return boundary | TYPE-PRODUCER-PLANNED — Protocol exists; no production producer yet; zero frozen types |

A consumer is counted only when executable repository code imports or receives the contract and produces an observable behavior. Synthetic consumers are forbidden. A contract moves to VERIFIED only after the legitimate producer/consumer relationship, contract tests, applicable CI gates, and evidence fingerprint are all established.

| `mtf_structure_alignment_boundary` | `shared.contracts.mtf_structure` | `analysis.mtf.deterministic_latest_point_alignment.DeterministicLatestPointAlignment` → `backtest.mtf_structure_replay.MtfStructureReplay` → `backtest.replay_engine.BacktestReplayEngine` | ACTIVE — deterministic methodology, replay consumer, and canonical Backtest integration |
| `backtest_mtf_structure_replay_boundary` | `backtest.mtf_structure_replay.MtfStructureReplay` | `backtest.replay_engine.BacktestReplayEngine` | ACTIVE — canonical replay integration |
