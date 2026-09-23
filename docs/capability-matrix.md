# Provider Capability Matrix

Architecture Frozen v1.0 — authoritative Provider Capability Matrix and Rate Limit Registry.

## Provider capability record schema

```yaml
provider: "<name>"
verified_at: "<UTC>"
evidence_source: "<official-documentation-reference>"
evidence_fingerprint: "<hash-or-equivalent>"
rest: "SUPPORTED|UNSUPPORTED|UNKNOWN"
websocket: "SUPPORTED|UNSUPPORTED|UNKNOWN"
authentication: "SUPPORTED|UNSUPPORTED|UNKNOWN"
sandbox_testnet: "SUPPORTED|UNSUPPORTED|UNKNOWN|N_A"
market_data: "SUPPORTED|UNSUPPORTED|UNKNOWN"
trading: "SUPPORTED|UNSUPPORTED|UNKNOWN|OUT_OF_SCOPE"
symbol_model: "<reference>"
rate_limit_ref: "<registry-id>"
api_contract_version: "<version-or-UNKNOWN>"
status: "VERIFIED|STALE|UNKNOWN"
```

## Capability baseline

| provider | status | rest | websocket | rate_limit_ref |
|---|---|---|---|---|
| Binance | UNKNOWN | UNKNOWN | UNKNOWN | rate_binance |
| Coinbase | UNKNOWN | UNKNOWN | UNKNOWN | rate_coinbase |
| Kraken | UNKNOWN | UNKNOWN | UNKNOWN | rate_kraken |
| KuCoin | UNKNOWN | UNKNOWN | UNKNOWN | rate_kucoin |
| OKX | UNKNOWN | UNKNOWN | UNKNOWN | rate_okx |
| Bybit | UNKNOWN | UNKNOWN | UNKNOWN | rate_bybit |
| Gate.io | UNKNOWN | UNKNOWN | UNKNOWN | rate_gateio |
| HTX | UNKNOWN | UNKNOWN | UNKNOWN | rate_htx |
| Bitfinex | UNKNOWN | UNKNOWN | UNKNOWN | rate_bitfinex |
| Bitstamp | UNKNOWN | UNKNOWN | UNKNOWN | rate_bitstamp |
| MEXC | UNKNOWN | UNKNOWN | UNKNOWN | rate_mexc |
| Crypto.com | UNKNOWN | UNKNOWN | UNKNOWN | rate_cryptocom |
| Bitget | UNKNOWN | UNKNOWN | UNKNOWN | rate_bitget |
| Gemini | UNKNOWN | UNKNOWN | UNKNOWN | rate_gemini |
| Upbit | UNKNOWN | UNKNOWN | UNKNOWN | rate_upbit |

UNKNOWN is intentional until current official provider documentation is verified. UNKNOWN MUST NOT be represented as implemented capability.

## Rate Limit Registry

| rate_limit_id | provider | scope | limit_model | status |
|---|---|---|---|---|
| rate_binance | Binance | provider-wide/endpoint-specific | UNKNOWN | UNKNOWN |
| rate_coinbase | Coinbase | provider-wide/endpoint-specific | UNKNOWN | UNKNOWN |
| rate_kraken | Kraken | provider-wide/endpoint-specific | UNKNOWN | UNKNOWN |
| rate_kucoin | KuCoin | provider-wide/endpoint-specific | UNKNOWN | UNKNOWN |
| rate_okx | OKX | provider-wide/endpoint-specific | UNKNOWN | UNKNOWN |
| rate_bybit | Bybit | provider-wide/endpoint-specific | UNKNOWN | UNKNOWN |
| rate_gateio | Gate.io | provider-wide/endpoint-specific | UNKNOWN | UNKNOWN |
| rate_htx | HTX | provider-wide/endpoint-specific | UNKNOWN | UNKNOWN |
| rate_bitfinex | Bitfinex | provider-wide/endpoint-specific | UNKNOWN | UNKNOWN |
| rate_bitstamp | Bitstamp | provider-wide/endpoint-specific | UNKNOWN | UNKNOWN |
| rate_mexc | MEXC | provider-wide/endpoint-specific | UNKNOWN | UNKNOWN |
| rate_cryptocom | Crypto.com | provider-wide/endpoint-specific | UNKNOWN | UNKNOWN |
| rate_bitget | Bitget | provider-wide/endpoint-specific | UNKNOWN | UNKNOWN |
| rate_gemini | Gemini | provider-wide/endpoint-specific | UNKNOWN | UNKNOWN |
| rate_upbit | Upbit | provider-wide/endpoint-specific | UNKNOWN | UNKNOWN |

Provider capability and rate-limit records require official evidence before becoming VERIFIED.
