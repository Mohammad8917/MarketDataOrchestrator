"""Live Binance provider smoke check.

This is an external connectivity smoke test, not a G01-G07 compliance gate.
"""

import asyncio
from datetime import datetime, timedelta, timezone

from ingestion.providers.binance_provider import BinanceProvider


def main() -> None:
    end = datetime.now(timezone.utc).replace(microsecond=0)
    start = end - timedelta(minutes=2)
    events = asyncio.run(BinanceProvider(interval="1m").fetch("BTCUSDT", start=start, end=end))
    if not events:
        raise SystemExit("Binance live smoke returned no kline events")
    if any(event.provider != "binance" or event.symbol != "BTCUSDT" for event in events):
        raise SystemExit("Binance live smoke returned invalid provider events")
    print(f"BINANCE LIVE SMOKE PASS: {len(events)} events")


if __name__ == "__main__":
    main()
