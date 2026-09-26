"""FILE: tests/regression/test_ingestion_regression.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-09-27
RESPONSIBILITY: Protect normalized market-data identity and provider provenance against regression.
LAYER: tests
OWNS: Ingestion contract regression verification.
DOES_NOT_OWN: Production ingestion behavior or provider transport.
DEPENDENCIES: datetime, decimal, domain.common.timeframe, domain.market_data_event
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from domain.common.timeframe import Timeframe
from domain.market_data_event import MarketDataEvent


def test_market_data_event_identity_and_provenance_are_canonical() -> None:
    now = datetime(2026, 9, 24, tzinfo=timezone.utc)
    event = MarketDataEvent.create(
        provider="provider-a",
        symbol="BTCUSDT",
        timeframe=Timeframe.parse("1m"),
        event_time=now,
        received_at=now,
        open=Decimal("100"),
        high=Decimal("110"),
        low=Decimal("90"),
        close=Decimal("105"),
        volume=Decimal("12.5"),
    )
    assert event.provider == "provider-a"
    assert event.symbol == "BTCUSDT"
    assert event.event_id.version == 5


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("provider", ""),
        ("symbol", ""),
    ],
)
def test_market_data_event_rejects_missing_identity(field: str, value: str) -> None:
    now = datetime(2026, 9, 24, tzinfo=timezone.utc)
    kwargs = {
        "provider": "provider-a",
        "symbol": "BTCUSDT",
        "timeframe": Timeframe.parse("1m"),
        "event_time": now,
        "received_at": now,
        "open": Decimal("100"),
        "high": Decimal("110"),
        "low": Decimal("90"),
        "close": Decimal("105"),
        "volume": Decimal("12.5"),
    }
    kwargs[field] = value
    with pytest.raises(ValueError):
        MarketDataEvent.create(**kwargs)
