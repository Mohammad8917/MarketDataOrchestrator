# Consumer Matrix

Architecture Frozen v1.0 — contract producer/consumer inventory.

| Contract | Producer | Consumer(s) found in repository | Verification status |
|---|---|---|---|
| `market_data_event` | `domain.market_data_event.MarketDataEvent` | None found at current HEAD | NOT VERIFIED — orphan pending legitimate consumer |
| `ingestion_provider_boundary` | Not implemented | None found | NOT VERIFIED |
| `provenance_metadata` | Not implemented | None found | NOT VERIFIED |
| `temporal_event_boundary` | Ownership unresolved | None found | NOT VERIFIED |
| `validation_result` | Not implemented | None found | NOT VERIFIED |

Consumer absence is not converted into a synthetic consumer. A contract may only move to verified status after a legitimate producer/consumer relationship is established or an explicit architecture decision authorizes an interface-only contract.
