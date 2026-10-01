"""Live Binance provider smoke check.

This is an external connectivity smoke test, not a G01-G07 compliance gate.
"""

import asyncio
from datetime import datetime, timedelta, timezone

from domain.common.timeframe import Timeframe
from domain.market_data_request import MarketDataRequest
from domain.market_scope import MarketScope
from ingestion.providers.binance_provider import BinanceProvider


def main() -> None:
    end = datetime.now(timezone.utc).replace(microsecond=0)
    start = end - timedelta(minutes=2)
    request = MarketDataRequest(
        market=MarketScope.CRYPTO,
        symbol="BTCUSDT",
        timeframe=Timeframe.parse("1m"),
        start=start,
        end=end,
    )
    events = asyncio.run(BinanceProvider(interval="1m").fetch(request))
    if not events:
        raise SystemExit("Binance live smoke returned no kline events")
    if any(event.provider != "binance" or event.symbol != "BTCUSDT" for event in events):
        raise SystemExit("Binance live smoke returned invalid provider events")
    print(f"BINANCE LIVE SMOKE PASS: {len(events)} events")


if __name__ == "__main__":
    main()
