"""FILE: persistence/market_data_store.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Persist and replay canonical MarketDataEvent values through SQLite.
LAYER: persistence
OWNS: SQLite storage, event serialization, idempotent writes, and deterministic replay.
DOES_NOT_OWN: provider transport, domain semantics, strategy logic, decision logic, risk policy, output formatting
DEPENDENCIES: sqlite3, datetime, decimal, pathlib, uuid, domain.market_data_event, domain.common.timeframe
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from domain.common.timeframe import Timeframe
from domain.market_data_event import MarketDataEvent


class MarketDataStore:
    def __init__(self, path: str | Path) -> None:
        self._connection = sqlite3.connect(str(path))
        self._connection.execute(
            "CREATE TABLE IF NOT EXISTS market_data_events "
            "(event_id TEXT PRIMARY KEY, provider TEXT NOT NULL, symbol TEXT NOT NULL, "
            "timeframe TEXT NOT NULL, event_time TEXT NOT NULL, received_at TEXT NOT NULL, "
            "open TEXT NOT NULL, high TEXT NOT NULL, low TEXT NOT NULL, "
            "close TEXT NOT NULL, volume TEXT NOT NULL)"
        )
        self._connection.commit()

    def write(self, event: MarketDataEvent) -> None:
        if not isinstance(event, MarketDataEvent):
            raise TypeError("event must be a MarketDataEvent")
        self._connection.execute(
            "INSERT OR IGNORE INTO market_data_events "
            "(event_id, provider, symbol, timeframe, event_time, received_at, open, high, low, close, volume) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (str(event.event_id), event.provider, event.symbol, event.timeframe.code,
             event.event_time.isoformat(), event.received_at.isoformat(),
             str(event.open), str(event.high), str(event.low), str(event.close), str(event.volume)),
        )
        self._connection.commit()

    def read_all(self) -> tuple[MarketDataEvent, ...]:
        rows = self._connection.execute(
            "SELECT event_id, provider, symbol, timeframe, event_time, received_at, "
            "open, high, low, close, volume FROM market_data_events "
            "ORDER BY event_time ASC, event_id ASC"
        ).fetchall()
        return tuple(self._row_to_event(row) for row in rows)

    @staticmethod
    def _parse_utc(value: str) -> datetime:
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            raise ValueError("stored datetime must be timezone-aware")
        return parsed.astimezone(timezone.utc)

    @classmethod
    def _row_to_event(cls, row: tuple[object, ...]) -> MarketDataEvent:
        event_id, provider, symbol, timeframe, event_time, received_at, open_value, high_value, low_value, close_value, volume = row
        return MarketDataEvent(
            event_id=UUID(str(event_id)),
            provider=str(provider),
            symbol=str(symbol),
            timeframe=Timeframe.parse(str(timeframe)),
            event_time=cls._parse_utc(str(event_time)),
            received_at=cls._parse_utc(str(received_at)),
            open=Decimal(str(open_value)),
            high=Decimal(str(high_value)),
            low=Decimal(str(low_value)),
            close=Decimal(str(close_value)),
            volume=Decimal(str(volume)),
        )

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> "MarketDataStore":
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        self.close()
