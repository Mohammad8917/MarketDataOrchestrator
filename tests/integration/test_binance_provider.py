"""FILE: tests/integration/test_binance_provider.py
RESPONSIBILITY: Verify the Binance provider against the canonical MarketDataEvent boundary.
"""

from __future__ import annotations

import asyncio
import json
from unittest.mock import patch

from ingestion.interfaces.market_provider import MarketDataProvider
from ingestion.providers.binance_provider import BinanceProvider


class _MockResponse:
    def __init__(self, payload: object) -> None:
        self._payload = json.dumps(payload).encode("utf-8")

    def __enter__(self) -> "_MockResponse":
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        return None

    def read(self) -> bytes:
        return self._payload


def test_binance_provider_satisfies_market_provider_protocol() -> None:
    assert isinstance(BinanceProvider(), MarketDataProvider)


def test_binance_provider_normalizes_mocked_klines() -> None:
    payload = [
        [
            1728000000000,
            "60000.10",
            "60500.20",
            "59900.00",
            "60300.30",
            "123.456",
            1728014399999,
            "7430000.00",
            100,
            "61.0",
            "3670000.00",
            "0",
        ]
    ]

    with patch(
        "ingestion.providers.binance_provider.urlopen",
        return_value=_MockResponse(payload),
    ) as mock_urlopen:
        events = asyncio.run(
            BinanceProvider(interval="4h", limit=1).fetch(
                "BTCUSDT",
                interval="4h",
                limit=1,
            )
        )

    assert len(events) == 1
    event = events[0]
    assert event.provider == "binance"
    assert event.symbol == "BTCUSDT"
    assert event.timeframe.code == "4h"
    assert str(event.open) == "60000.10"
    assert str(event.high) == "60500.20"
    assert str(event.low) == "59900.00"
    assert str(event.close) == "60300.30"
    assert str(event.volume) == "123.456"
    assert event.event_time.tzinfo is not None
    assert event.event_time.utcoffset().total_seconds() == 0
    assert event.event_id.version == 5

    request = mock_urlopen.call_args.args[0]
    assert "symbol=BTCUSDT" in request.full_url
    assert "interval=4h" in request.full_url
    assert "limit=1" in request.full_url


def test_binance_provider_passes_utc_window() -> None:
    from datetime import datetime, timezone

    payload = []
    with patch(
        "ingestion.providers.binance_provider.urlopen",
        return_value=_MockResponse(payload),
    ) as mock_urlopen:
        asyncio.run(
            BinanceProvider(interval="4h", limit=10).fetch(
                "BTCUSDT",
                start=datetime(2026, 1, 1, tzinfo=timezone.utc),
                end=datetime(2026, 1, 2, tzinfo=timezone.utc),
            )
        )

    request = mock_urlopen.call_args.args[0]
    assert "startTime=1767225600000" in request.full_url
    assert "endTime=1767312000000" in request.full_url
