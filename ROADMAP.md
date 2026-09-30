# ROADMAP

> Provider inventory is canonical in config/exchanges.yaml.

## Product direction

Market Data → Data Quality → Time Alignment → Market Structure → Regime → Regime Uncertainty → Volatility → Strategy Sensors → Setup → MTF Confirmation → Liquidity/Cost/Expected Edge → Risk → Decision → Audit → Evaluation

## Markets

| Market | Current state |
|---|---|
| Crypto | Binance executable path present |
| Forex | Architecture target; provider implementation planned |
| Gold | Architecture target; provider implementation planned |

## Provider target — 15

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

Implemented: 1/15.

## Engineering order

1. Contract and methodology
2. Strong unit/contract tests
3. Persistence/infrastructure consumer
4. Engine and strategy analysis
5. Evaluation and metrics
6. Application/orchestration
7. Telegram/UI only after lower layers are executable

## Trading guardrails

- No Data Quality → No Analysis.
- No Valid Setup → No Trade.
- No Positive Net Edge → No Trade.
- Sensors describe market conditions; they do not independently own final BUY/SELL decisions.
