"""FILE: ingestion/providers/crypto/binance_provider.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-25
DATE_PERSIAN: 1405-07-03
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Fetch public Binance Spot candlestick data and translate it into the canonical market-provider event boundary.
LAYER: ingestion
OWNS: Binance public REST transport, kline pagination, response validation, and deterministic event identity.
DOES_NOT_OWN: analysis, indicators, strategy, decision, risk, persistence, credentials, order execution.
DEPENDENCIES: stdlib:datetime; stdlib:hashlib; stdlib:json; stdlib:typing; stdlib:urllib; ingestion.interfaces.market_provider
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from ingestion.interfaces.market_provider import MarketEvent


class BinanceProvider:
    """Binance Spot public-market provider using the canonical provider boundary."""

    provider_id = "binance"

    _BASE_URL = "https://data-api.binance.vision"
    _KLINES_PATH = "/api/v3/klines"
    _MAX_LIMIT = 1000
    _VALID_INTERVALS = frozenset(
        {"1s", "1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M"}
    )

    def __init__(
        self,
        *,
        interval: str = "1m",
        base_url: str = _BASE_URL,
        opener: Callable[..., Any] = urlopen,
        timeout_seconds: float = 10.0,
    ) -> None:
        if interval not in self._VALID_INTERVALS:
            raise ValueError(f"unsupported Binance interval: {interval}")
        if not base_url.strip():
            raise ValueError("base_url must be non-empty")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self._interval = interval
        self._base_url = base_url.rstrip("/")
        self._opener = opener
        self._timeout_seconds = timeout_seconds

    async def fetch(
        self, symbol: str, *, start: datetime, end: datetime
    ) -> tuple[MarketEvent, ...]:
        self._validate_window(symbol, start, end)
        start_ms = self._to_milliseconds(start)
        end_ms_exclusive = self._to_milliseconds(end)
        next_start = start_ms
        events: list[MarketEvent] = []

        while next_start < end_ms_exclusive:
            rows = self._fetch_page(
                symbol=symbol,
                start_ms=next_start,
                end_ms=end_ms_exclusive - 1,
            )
            if not rows:
                break

            for row in rows:
                event = self._event_from_kline(symbol, row)
                event_ms = self._to_milliseconds(event.event_time)
                if start_ms <= event_ms < end_ms_exclusive:
                    events.append(event)

            last_open_ms = int(rows[-1][0])
            if last_open_ms < next_start:
                raise RuntimeError("Binance returned non-monotonic kline data")
            if last_open_ms >= end_ms_exclusive - 1 or len(rows) < self._MAX_LIMIT:
                break
            next_start = last_open_ms + 1

        return tuple(sorted(events, key=lambda item: (item.event_time, item.source_event_id)))

    def _fetch_page(self, *, symbol: str, start_ms: int, end_ms: int) -> list[list[Any]]:
        query = urlencode(
            {
                "symbol": symbol.upper(),
                "interval": self._interval,
                "startTime": start_ms,
                "endTime": end_ms,
                "limit": self._MAX_LIMIT,
            }
        )
        request = Request(
            f"{self._base_url}{self._KLINES_PATH}?{query}",
            headers={"Accept": "application/json", "User-Agent": "MarketDataOrchestrator/0.1"},
            method="GET",
        )
        try:
            with self._opener(request, timeout=self._timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            retry_after = exc.headers.get("Retry-After")
            detail = f"HTTP {exc.code}"
            if retry_after:
                detail += f"; retry after {retry_after}s"
            raise RuntimeError(f"Binance kline request failed: {detail}") from exc
        except (URLError, TimeoutError, OSError, ValueError) as exc:
            raise RuntimeError("Binance kline request failed") from exc

        if not isinstance(payload, list):
            raise RuntimeError("Binance kline response must be a list")
        for row in payload:
            if not isinstance(row, list) or len(row) != 12:
                raise RuntimeError("Binance kline row must contain exactly 12 fields")
        return payload

    def _event_from_kline(self, symbol: str, row: list[Any]) -> MarketEvent:
        open_ms = row[0]
        if not isinstance(open_ms, int) or isinstance(open_ms, bool) or open_ms < 0:
            raise RuntimeError("Binance kline open time must be a non-negative integer")
        raw = json.dumps(row, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        digest = hashlib.sha256(raw).hexdigest()
        event_time = datetime.fromtimestamp(open_ms / 1000, tz=timezone.utc)
        return MarketEvent(
            source_event_id=f"binance:{symbol.upper()}:{open_ms}",
            source=self.provider_id,
            symbol=symbol.upper(),
            event_time=event_time,
            received_at=datetime.now(timezone.utc),
            payload_digest=f"sha256:{digest}",
        )

    @staticmethod
    def _validate_window(symbol: str, start: datetime, end: datetime) -> None:
        if not symbol.strip():
            raise ValueError("symbol must be non-empty")
        for value, name in ((start, "start"), (end, "end")):
            if value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
                raise ValueError(f"{name} must be timezone-aware UTC")
        if start >= end:
            raise ValueError("start must be before end")

    @staticmethod
    def _to_milliseconds(value: datetime) -> int:
        return int(value.timestamp() * 1000)

