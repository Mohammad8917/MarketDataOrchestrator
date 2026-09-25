"""FILE: tests/backtest/test_temporal_replay.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify deterministic historical ordering and temporal boundaries for replay.
LAYER: tests
OWNS: Backtest temporal replay verification.
DOES_NOT_OWN: Production backtest engine or market data providers.
DEPENDENCIES: pytest; ingestion.interfaces.market_provider
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timezone
from ingestion.interfaces.market_provider import MarketEvent


def test_historical_events_have_explicit_utc_temporal_order() -> None:
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    events = (
        MarketEvent("2", "fixture", "BTCUSDT", base.replace(second=2), base, "sha256:2"),
        MarketEvent("1", "fixture", "BTCUSDT", base.replace(second=1), base, "sha256:1"),
    )
    ordered = tuple(sorted(events, key=lambda item: (item.event_time, item.source_event_id)))
    assert [item.source_event_id for item in ordered] == ["1", "2"]
    assert all(item.event_time.tzinfo is not None for item in ordered)
