"""FILE: ingestion/providers/binance_provider.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-25
DATE_PERSIAN: 1405-07-03
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Fetch public Binance Spot klines and normalize them into canonical MarketDataEvent values.
LAYER: ingestion
OWNS: Binance public REST transport, response validation, and canonical event normalization.
DOES_NOT_OWN: persistence, strategy, backtesting, decision, risk, credentials, order execution.
DEPENDENCIES: asyncio, json, datetime, decimal, typing, urllib, domain.common.timeframe, domain.market_data_event, ingestion.interfaces.market_provider
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from decimal import Decimal
from collections.abc import Callable
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from domain.common.timeframe import Timeframe
from domain.market_data_event import MarketDataEvent
from ingestion.interfaces.market_provider import MarketDataProvider


class BinanceProviderError(RuntimeError):
    """Base error for Binance transport/provider failures."""


class BinanceRateLimitError(BinanceProviderError):
    """Raised when Binance rejects a request because of rate limiting."""


class BinanceTimeoutError(BinanceProviderError):
    """Raised when the Binance public API request times out."""


class BinanceProvider(MarketDataProvider):
    provider_id = "binance"
    BASE_URL = "https://api.binance.com/api/v3/klines"

    def __init__(
        self,
        *,
        interval: str = "4h",
        limit: int = 1000,
        timeout: float = 10.0,
        opener: Callable[..., Any] = urlopen,
    ) -> None:
        self._interval = Timeframe.parse(interval)
        if not 1 <= limit <= 1000:
            raise ValueError("limit must be between 1 and 1000")
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        self._limit = limit
        self._timeout = timeout
        self._opener = opener

    async def fetch(
        self,
        symbol: str,
        *,
        start: datetime,
        end: datetime,
    ) -> tuple[MarketDataEvent, ...]:
        """Fetch Binance klines and normalize them into canonical events."""
        if not isinstance(symbol, str) or not symbol.strip():
            raise ValueError("symbol must be a non-empty string")

        timeframe = self._interval
        request_limit = self._limit
        self._require_utc("start", start)
        self._require_utc("end", end)
        if start >= end:
            raise ValueError("start must be before end")

        params: dict[str, str] = {
            "symbol": symbol.upper(),
            "interval": timeframe.code,
            "limit": str(request_limit),
        }
        params["startTime"] = str(self._epoch_milliseconds(start))
        params["endTime"] = str(self._epoch_milliseconds(end))

        payload = await asyncio.to_thread(self._request_json, params)
        received_at = datetime.now(timezone.utc)
        return tuple(
            self._to_event(
                row,
                symbol=symbol.upper(),
                timeframe=timeframe,
                received_at=received_at,
            )
            for row in payload
        )

    def _request_json(self, params: dict[str, str]) -> list[Any]:
        request = Request(
            f"{self.BASE_URL}?{urlencode(params)}",
            headers={"Accept": "application/json", "User-Agent": "MarketDataOrchestrator/0.1"},
            method="GET",
        )
        try:
            with self._opener(request, timeout=self._timeout) as response:
                raw = response.read()
        except HTTPError as exc:
            if exc.code in (429, 418):
                raise BinanceRateLimitError(
                    f"Binance rate limit response: HTTP {exc.code}"
                ) from exc
            raise BinanceProviderError(f"Binance HTTP error: HTTP {exc.code}") from exc
        except TimeoutError as exc:
            raise BinanceTimeoutError("Binance request timed out") from exc
        except URLError as exc:
            if isinstance(exc.reason, TimeoutError):
                raise BinanceTimeoutError("Binance request timed out") from exc
            raise BinanceProviderError("Binance network request failed") from exc

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise BinanceProviderError("Binance returned invalid JSON") from exc

        if not isinstance(payload, list):
            raise BinanceProviderError("Binance returned an unexpected payload")
        return payload

    @classmethod
    def _to_event(
        cls,
        row: Any,
        *,
        symbol: str,
        timeframe: Timeframe,
        received_at: datetime,
    ) -> MarketDataEvent:
        if not isinstance(row, list) or len(row) < 6:
            raise BinanceProviderError("Binance kline row has an invalid shape")
        try:
            event_time = datetime.fromtimestamp(int(row[0]) / 1000, tz=timezone.utc)
            open_value = Decimal(str(row[1]))
            high_value = Decimal(str(row[2]))
            low_value = Decimal(str(row[3]))
            close_value = Decimal(str(row[4]))
            volume = Decimal(str(row[5]))
        except (TypeError, ValueError, ArithmeticError) as exc:
            raise BinanceProviderError("Binance kline row contains invalid values") from exc

        try:
            return MarketDataEvent.create(
                provider=cls.provider_id,
                symbol=symbol,
                timeframe=timeframe,
                event_time=event_time,
                received_at=received_at,
                open=open_value,
                high=high_value,
                low=low_value,
                close=close_value,
                volume=volume,
            )
        except ValueError as exc:
            raise BinanceProviderError("Binance kline row violates market-data invariants") from exc

    @staticmethod
    def _require_utc(name: str, value: datetime) -> None:
        if value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
            raise ValueError(f"{name} must be timezone-aware UTC")

    @staticmethod
    def _epoch_milliseconds(value: datetime) -> int:
        return int(value.timestamp() * 1000)
