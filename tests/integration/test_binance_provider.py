"""FILE: tests/integration/test_binance_provider.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-25
DATE_PERSIAN: 1405-07-03
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify Binance public REST pagination, normalization, identity stability, and boundary isolation.
LAYER: tests
OWNS: Binance provider integration verification.
DOES_NOT_OWN: Binance transport implementation, exchange availability, production credentials.
DEPENDENCIES: stdlib:datetime; stdlib:json; pytest; ingestion.providers.crypto.binance_provider; ingestion.interfaces.market_provider
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timezone
from typing import Any
from urllib.parse import parse_qs, urlparse

import pytest

from ingestion.interfaces.market_provider import MarketDataProvider
from ingestion.providers.crypto.binance_provider import BinanceProvider


class FakeResponse:
    def __init__(self, payload: list[list[Any]]) -> None:
        self._payload = payload

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        import json

        return json.dumps(self._payload).encode("utf-8")


def test_binance_provider_satisfies_market_provider_protocol() -> None:
    assert isinstance(BinanceProvider(), MarketDataProvider)


@pytest.mark.asyncio
async def test_binance_provider_rejects_invalid_interval_and_window() -> None:
    with pytest.raises(ValueError, match="unsupported Binance interval"):
        BinanceProvider(interval="9m")
    provider = BinanceProvider()
    with pytest.raises(ValueError, match="start must be timezone-aware UTC"):
        await provider.fetch(
            "BTCUSDT",
            start=datetime(2026, 9, 25, 9),
            end=datetime(2026, 9, 25, 10, tzinfo=timezone.utc),
        )


@pytest.mark.asyncio
async def test_binance_provider_fetches_and_paginates_klines() -> None:
    rows = [
        [1000, "1", "2", "0.5", "1.5", "10", 1999, "15", 2, "5", "7", "0"],
        [2000, "1.5", "2.5", "1", "2", "11", 2999, "20", 3, "6", "8", "0"],
    ]
    calls: list[str] = []

    def opener(request: Any, *, timeout: float) -> FakeResponse:
        calls.append(request.full_url)
        query = parse_qs(urlparse(request.full_url).query)
        assert query["symbol"] == ["BTCUSDT"]
        assert query["interval"] == ["1m"]
        assert query["limit"] == ["1000"]
        return FakeResponse(rows)

    result = await BinanceProvider(opener=opener).fetch(
        "btcusdt",
        start=datetime.fromtimestamp(1, tz=timezone.utc),
        end=datetime.fromtimestamp(3, tz=timezone.utc),
    )

    assert len(result) == 2
    assert [event.source_event_id for event in result] == [
        "binance:BTCUSDT:1000",
        "binance:BTCUSDT:2000",
    ]
    assert all(event.source == "binance" for event in result)
    assert all(event.symbol == "BTCUSDT" for event in result)
    assert all(event.payload_digest.startswith("sha256:") for event in result)
    assert len(calls) == 1


@pytest.mark.asyncio
async def test_binance_provider_paginates_full_pages() -> None:
    first = [
        [index * 1000, "1", "2", "0.5", "1.5", "10", index * 1000 + 999, "15", 2, "5", "7", "0"]
        for index in range(1000)
    ]
    second = [[1_000_000, "1", "2", "0.5", "1.5", "10", 1_000_999, "15", 2, "5", "7", "0"]]
    payloads = [first, second]
    seen_starts: list[str] = []

    def opener(request: Any, *, timeout: float) -> FakeResponse:
        query = parse_qs(urlparse(request.full_url).query)
        seen_starts.append(query["startTime"][0])
        return FakeResponse(payloads.pop(0))

    result = await BinanceProvider(opener=opener).fetch(
        "BTCUSDT",
        start=datetime.fromtimestamp(0, tz=timezone.utc),
        end=datetime.fromtimestamp(1_001, tz=timezone.utc),
    )

    assert len(result) == 1001
    assert seen_starts == ["0", "1000000"]


@pytest.mark.asyncio
async def test_binance_provider_rejects_malformed_rows() -> None:
    def opener(request: Any, *, timeout: float) -> FakeResponse:
        return FakeResponse([[1, "bad"]])

    with pytest.raises(RuntimeError, match="exactly 12 fields"):
        await BinanceProvider(opener=opener).fetch(
            "BTCUSDT",
            start=datetime.fromtimestamp(0, tz=timezone.utc),
            end=datetime.fromtimestamp(2, tz=timezone.utc),
        )
