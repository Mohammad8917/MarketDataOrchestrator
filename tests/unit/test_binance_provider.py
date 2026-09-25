import asyncio
import json
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError

import pytest

from ingestion.providers.binance_provider import (
    BinanceProvider,
    BinanceProviderError,
    BinanceRateLimitError,
    BinanceTimeoutError,
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


def window() -> tuple[datetime, datetime]:
    return (
        datetime(2026, 1, 1, tzinfo=timezone.utc),
        datetime(2026, 1, 2, tzinfo=timezone.utc),
    )


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

    start, end = window()
    return asyncio.run(
        BinanceProvider(interval="4h", limit=1, opener=opener).fetch(
            "btcusdt", start=start, end=end
        )
    )


@pytest.mark.parametrize("limit", (0, 1001))
def test_rejects_invalid_limit(limit: int) -> None:
    with pytest.raises(ValueError, match="between 1 and 1000"):
        BinanceProvider(limit=limit)


def test_rejects_non_positive_timeout() -> None:
    with pytest.raises(ValueError, match="timeout"):
        BinanceProvider(timeout=0)


@pytest.mark.parametrize(
    ("symbol", "start", "end"),
    [
        ("", *window()),
        ("   ", *window()),
        ("BTCUSDT", datetime(2026, 1, 1), window()[1]),
        ("BTCUSDT", window()[0], datetime(2026, 1, 2)),
        ("BTCUSDT", window()[1], window()[0]),
    ],
)
def test_rejects_invalid_request_window(symbol, start, end) -> None:
    with pytest.raises(ValueError):
        asyncio.run(BinanceProvider().fetch(symbol, start=start, end=end))


def test_normalizes_row_and_uppercases_symbol() -> None:
    events = call([valid_row()])
    assert len(events) == 1
    assert events[0].symbol == "BTCUSDT"


@pytest.mark.parametrize("status", (418, 429, 500))
def test_maps_http_errors(status: int) -> None:
    def opener(request, *, timeout):
        raise HTTPError(request.full_url, status, "error", {}, None)

    start, end = window()
    expected = BinanceRateLimitError if status in (418, 429) else BinanceProviderError
    with pytest.raises(expected):
        asyncio.run(
            BinanceProvider(opener=opener).fetch("BTCUSDT", start=start, end=end)
        )


def test_maps_timeout_and_network_errors() -> None:
    def timeout_opener(request, *, timeout):
        raise TimeoutError()

    def url_timeout_opener(request, *, timeout):
        raise URLError(TimeoutError())

    start, end = window()
    with pytest.raises(BinanceTimeoutError):
        asyncio.run(
            BinanceProvider(opener=timeout_opener).fetch(
                "BTCUSDT", start=start, end=end
            )
        )
    with pytest.raises(BinanceTimeoutError):
        asyncio.run(
            BinanceProvider(opener=url_timeout_opener).fetch(
                "BTCUSDT", start=start, end=end
            )
        )


def test_maps_other_network_errors() -> None:
    def opener(request, *, timeout):
        raise URLError("connection refused")

    start, end = window()
    with pytest.raises(BinanceProviderError, match="network"):
        asyncio.run(
            BinanceProvider(opener=opener).fetch("BTCUSDT", start=start, end=end)
        )


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

    start, end = window()
    with pytest.raises(BinanceProviderError):
        asyncio.run(
            BinanceProvider(opener=opener).fetch("BTCUSDT", start=start, end=end)
        )


@pytest.mark.parametrize(
    "row",
    [
        [],
        [1, "100", "110"],
        [1, "100", "not-a-number", "90", "105", "1"],
    ],
)
def test_rejects_malformed_rows(row: list[object]) -> None:
    with pytest.raises(BinanceProviderError):
        call([row])
