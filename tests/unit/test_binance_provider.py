import asyncio
import json
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError, URLError

import pytest

from domain.common.timeframe import Timeframe
from domain.market_data_request import MarketDataRequest
from domain.market_scope import MarketScope
from ingestion.providers.binance_provider import (
    BinanceProvider,
    BinanceProviderError,
    BinanceRateLimitError,
    BinanceTimeoutError,
)


def request(
    *,
    symbol: str = "BTCUSDT",
    timeframe: str = "4h",
    market: MarketScope = MarketScope.CRYPTO,
) -> MarketDataRequest:
    return MarketDataRequest(
        market=market,
        symbol=symbol,
        timeframe=Timeframe.parse(timeframe),
        start=datetime(2026, 1, 1, tzinfo=timezone.utc),
        end=datetime(2026, 1, 2, tzinfo=timezone.utc),
    )


class Response:
    def __init__(self, payload: object, *, raw: bytes | None = None) -> None:
        self.payload = payload
        self.raw = raw

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return None

    def read(self) -> bytes:
        return self.raw if self.raw is not None else json.dumps(self.payload).encode()


def valid_row() -> list[object]:
    return [
        1767225600000,
        "100",
        "110",
        "90",
        "105",
        "12.5",
        1767239999999,
        "0",
        1,
        "0",
        "0",
        "0",
    ]


def call(payload: object):
    def opener(request, *, timeout):
        return Response(payload)

    return asyncio.run(
        BinanceProvider(interval="4h", limit=1, opener=opener).fetch(request(symbol="btcusdt"))
    )


@pytest.mark.parametrize("limit", (0, 1001))
def test_rejects_invalid_limit(limit: int) -> None:
    with pytest.raises(ValueError, match="between 1 and 1000"):
        BinanceProvider(limit=limit)


def test_rejects_non_positive_timeout() -> None:
    with pytest.raises(ValueError, match="timeout"):
        BinanceProvider(timeout=0)


def test_rejects_non_crypto_market_scope() -> None:
    with pytest.raises(ValueError, match="only the crypto market scope"):
        asyncio.run(
            BinanceProvider().fetch(request(market=MarketScope.FOREX))
        )


def test_rejects_mismatched_timeframe() -> None:
    with pytest.raises(ValueError, match="must match provider interval 4h"):
        asyncio.run(
            BinanceProvider(interval="4h").fetch(request(timeframe="1h"))
        )


def test_normalizes_row_and_uppercases_symbol() -> None:
    events = call([valid_row()])
    assert len(events) == 1
    assert events[0].symbol == "BTCUSDT"


@pytest.mark.parametrize("status", (418, 429, 500))
def test_maps_http_errors(status: int) -> None:
    def opener(request, *, timeout):
        raise HTTPError(request.full_url, status, "error", {}, None)

    expected = BinanceRateLimitError if status in (418, 429) else BinanceProviderError
    with pytest.raises(expected):
        asyncio.run(BinanceProvider(opener=opener).fetch(request()))


def test_maps_timeout_and_network_errors() -> None:
    def timeout_opener(request, *, timeout):
        raise TimeoutError()

    def url_timeout_opener(request, *, timeout):
        raise URLError(TimeoutError())

    with pytest.raises(BinanceTimeoutError):
        asyncio.run(BinanceProvider(opener=timeout_opener).fetch(request()))
    with pytest.raises(BinanceTimeoutError):
        asyncio.run(BinanceProvider(opener=url_timeout_opener).fetch(request()))


def test_maps_other_network_errors() -> None:
    def opener(request, *, timeout):
        raise URLError("connection refused")

    with pytest.raises(BinanceProviderError, match="network"):
        asyncio.run(BinanceProvider(opener=opener).fetch(request()))


@pytest.mark.parametrize(
    "raw",
    [
        b"not-json",
        json.dumps({"error": "bad"}).encode(),
    ],
)
def test_rejects_invalid_payloads(raw: bytes) -> None:
    def opener(request, *, timeout):
        return Response(None, raw=raw)

    with pytest.raises(BinanceProviderError):
        asyncio.run(BinanceProvider(opener=opener).fetch(request()))


@pytest.mark.parametrize(
    "row",
    [
        [],
        [1, "100", "110"],
        [1, "100", "not-a-number", "90", "105", "1"],
        [1, "100", "90", "95", "105", "1"],
        [1, "100", "110", "90", "105", "-1"],
        [1, "NaN", "110", "90", "105", "1"],
        [1, "100", "Infinity", "90", "105", "1"],
    ],
)
def test_rejects_malformed_rows(row: list[object]) -> None:
    with pytest.raises(BinanceProviderError):
        call([row])
