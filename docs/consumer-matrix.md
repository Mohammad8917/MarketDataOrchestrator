# Consumer Matrix

Architecture Frozen v1.0 — contract producer/consumer inventory.

| Contract | Producer | Consumer(s) found in repository | Verification status |
|---|---|---|---|
| `market_data_event` | `domain.market_data_event.MarketDataEvent` | `persistence.market_data_store.MarketDataStore` | ACTIVE — CI evidence pending |
| `market_data_store` (component output) | `persistence.market_data_store.MarketDataStore.read_all()` | `backtest.engine.BacktestEngine.run()` typed input boundary | TYPE-CONSUMER-PLANNED — interface exists; no production implementation calls `read_all()` yet |
| `ingestion_provider_boundary` | Not implemented | None found | NOT VERIFIED |
| `provenance_metadata` | Not implemented | None found | NOT VERIFIED |
| `temporal_event_boundary` | Ownership unresolved | None found | NOT VERIFIED |
| `validation_result` | Not implemented | None found | NOT VERIFIED |

A consumer is counted only when executable repository code imports or receives the contract and produces an observable behavior. Synthetic consumers are forbidden. A contract moves to VERIFIED only after the legitimate producer/consumer relationship, contract tests, applicable CI gates, and evidence fingerprint are all established.
