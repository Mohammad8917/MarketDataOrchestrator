"""FILE: tests/backtest/test_temporal_replay.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-09-27
RESPONSIBILITY: Verify deterministic historical ordering and temporal boundaries for replay.
LAYER: tests
OWNS: Backtest temporal replay verification.
DOES_NOT_OWN: Production backtest engine or market data providers.
DEPENDENCIES: datetime, decimal, domain.common.timeframe, domain.market_data_event
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timezone
from decimal import Decimal

from domain.common.timeframe import Timeframe
from domain.market_data_event import MarketDataEvent


def test_historical_events_have_explicit_utc_temporal_order() -> None:
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    timeframe = Timeframe.parse("1s")
    events = (
        MarketDataEvent.create(
            provider="fixture",
            symbol="BTCUSDT",
            timeframe=timeframe,
            event_time=base.replace(second=2),
            received_at=base.replace(second=2),
            open=Decimal("102"),
            high=Decimal("102"),
            low=Decimal("102"),
            close=Decimal("102"),
            volume=Decimal("1"),
        ),
        MarketDataEvent.create(
            provider="fixture",
            symbol="BTCUSDT",
            timeframe=timeframe,
            event_time=base.replace(second=1),
            received_at=base.replace(second=1),
            open=Decimal("101"),
            high=Decimal("101"),
            low=Decimal("101"),
            close=Decimal("101"),
            volume=Decimal("1"),
        ),
    )
    ordered = tuple(sorted(events, key=lambda item: (item.event_time, item.event_id)))
    assert [item.event_time.second for item in ordered] == [1, 2]
    assert all(item.event_time.tzinfo is not None for item in ordered)
