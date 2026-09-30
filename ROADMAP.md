# ROADMAP

> Provider inventory is machine-readable in config/exchanges.yaml.

## Product direction

Build the trading-analysis system bottom-up: market data → quality → time alignment → market structure → regime → sensors → setup → confirmation → liquidity/cost/edge → risk → decision → audit → evaluation.

## Markets

| Market | Current repository status |
|---|---|
| Crypto | Binance provider implemented; broader provider expansion planned |
| Forex | Architecture target; provider implementation planned |
| Gold | Architecture target; provider implementation planned |

## Provider target — 15

Implemented: 1/15

| # | Provider | Status |
|---:|---|---|
| 1 | Binance | implemented |
| 2 | Coinbase | planned |
| 3 | Kraken | planned |
| 4 | OKX | planned |
| 5 | Bybit | planned |
| 6 | Bitstamp | planned |
| 7 | KuCoin | planned |
| 8 | Gate.io | planned |
| 9 | Bitfinex | planned |
| 10 | Gemini | planned |
| 11 | Bitget | planned |
| 12 | MEXC | planned |
| 13 | HTX | planned |
| 14 | Crypto.com | planned |
| 15 | CEX.IO | planned |

## Engineering order

1. Contract and methodology
2. Strong unit/contract tests
3. Persistence/infrastructure consumer
4. Engine and strategy analysis
5. Evaluation and metrics
6. Application/orchestration
7. Telegram/UI only after lower layers are executable

## Guardrails

- No Data Quality → No Analysis.
- No Valid Setup → No Trade.
- No Positive Net Edge → No Trade.
- G01–G07 remain compliance guardrails; they do not replace product development.
