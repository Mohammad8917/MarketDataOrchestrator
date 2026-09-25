"""FILE: tests/regression/test_ingestion_regression.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Protect normalized market-event identity and source provenance against regression.
LAYER: tests
OWNS: Ingestion contract regression verification.
DOES_NOT_OWN: Production ingestion behavior or provider transport.
DEPENDENCIES: pytest; ingestion.interfaces.market_provider
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timezone
import pytest
from ingestion.interfaces.market_provider import MarketEvent


def test_market_event_identity_and_provenance_are_required() -> None:
    now = datetime(2026, 9, 24, tzinfo=timezone.utc)
    event = MarketEvent("evt-1", "provider-a", "BTCUSDT", now, now, "sha256:abc")
    assert event.source_event_id == "evt-1"
    assert event.source == "provider-a"
    assert event.payload_digest == "sha256:abc"


@pytest.mark.parametrize("field", ["source_event_id", "source", "symbol", "payload_digest"])
def test_market_event_rejects_missing_identity(field: str) -> None:
    now = datetime(2026, 9, 24, tzinfo=timezone.utc)
    values = {
        "source_event_id": "evt-1",
        "source": "provider-a",
        "symbol": "BTCUSDT",
        "payload_digest": "sha256:abc",
    }
    values[field] = ""
    with pytest.raises(ValueError):
        MarketEvent(
            values["source_event_id"],
            values["source"],
            values["symbol"],
            now,
            now,
            values["payload_digest"],
        )
