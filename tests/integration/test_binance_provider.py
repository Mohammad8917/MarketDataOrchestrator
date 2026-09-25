"""FILE: tests/integration/test_binance_provider.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-09-25
DATE_PERSIAN: 1405-07-03
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify the Binance provider against the canonical MarketDataEvent boundary.
LAYER: tests
OWNS: Binance provider integration verification.
DOES_NOT_OWN: Binance transport implementation, exchange availability, production credentials.
DEPENDENCIES: stdlib:asyncio, stdlib:datetime, stdlib:json, stdlib:typing, ingestion.interfaces.market_provider, ingestion.providers.binance_provider
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timedelta, timezone
from typing import Any

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

    calls: list[Any] = []

    def opener(request: Any, *, timeout: float) -> _MockResponse:
        calls.append(request)
        return _MockResponse(payload)

    events = asyncio.run(
        BinanceProvider(interval="4h", limit=1, opener=opener).fetch(
            "BTCUSDT",
            start=datetime(2024, 10, 4, tzinfo=timezone.utc),
            end=datetime(2024, 10, 5, tzinfo=timezone.utc),
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
    assert event.event_time.utcoffset() == timedelta(0)
    assert event.event_id.version == 5

    request = calls[0]
    assert "symbol=BTCUSDT" in request.full_url
    assert "interval=4h" in request.full_url
    assert "limit=1" in request.full_url


def test_binance_provider_passes_utc_window() -> None:
    payload: list[object] = []
    calls: list[object] = []

    def opener(request: object, *, timeout: float) -> _MockResponse:
        calls.append(request)
        return _MockResponse(payload)

    asyncio.run(
        BinanceProvider(interval="4h", limit=10, opener=opener).fetch(
            "BTCUSDT",
            start=datetime(2026, 1, 1, tzinfo=timezone.utc),
            end=datetime(2026, 1, 2, tzinfo=timezone.utc),
        )
    )

    request = calls[0]
    assert "startTime=1767225600000" in request.full_url
    assert "endTime=1767312000000" in request.full_url
