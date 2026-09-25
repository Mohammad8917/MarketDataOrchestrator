"""FILE: tests/contract/test_provider_contract.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.2
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify the canonical asynchronous market-data provider contract and normalized event invariants.
LAYER: tests
OWNS: Provider boundary contract verification.
DOES_NOT_OWN: Provider transport, retries, credentials, persistence, analysis, strategy, decision, risk.
DEPENDENCIES: stdlib:datetime; stdlib:typing; pytest; ingestion.interfaces.market_provider
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from typing import Any, cast

import pytest

from ingestion.interfaces.market_provider import MarketDataProvider, MarketEvent


class ContractProvider:
    provider_id = "contract-provider"

    async def fetch(
        self, symbol: str, *, start: datetime, end: datetime
    ) -> tuple[MarketEvent, ...]:
        return ()


class InvalidContractProvider:
    async def fetch(
        self, symbol: str, *, start: datetime, end: datetime
    ) -> tuple[MarketEvent, ...]:
        return ()


def test_market_data_provider_is_runtime_protocol() -> None:
    assert isinstance(ContractProvider(), MarketDataProvider)


def test_invalid_provider_is_rejected_by_runtime_protocol() -> None:
    assert not isinstance(InvalidContractProvider(), MarketDataProvider)


def test_market_event_declares_frozen_dataclass() -> None:
    assert getattr(MarketEvent, "__dataclass_params__").frozen is True


def test_market_event_is_immutable_and_slotted() -> None:
    event = MarketEvent(
        "evt-1",
        "provider",
        "BTCUSDT",
        datetime(2026, 9, 24, 9, tzinfo=timezone.utc),
        datetime(2026, 9, 24, 9, 1, tzinfo=timezone.utc),
        "sha256:abc",
    )
    # Intentionally bypass static check to verify runtime immutability.
    with pytest.raises(FrozenInstanceError):
        cast(Any, event).symbol = "ETHUSDT"
    assert hasattr(event, "__slots__")
    assert not hasattr(event, "__dict__")


@pytest.mark.parametrize(
    "field, value",
    [
        ("source_event_id", ""),
        ("source", ""),
        ("symbol", ""),
    ],
)
def test_market_event_rejects_missing_identity(field: str, value: str) -> None:
    values: dict[str, Any] = {
        "source_event_id": "evt-1",
        "source": "provider",
        "symbol": "BTCUSDT",
        "event_time": datetime(2026, 9, 24, 9, tzinfo=timezone.utc),
        "received_at": datetime(2026, 9, 24, 9, 1, tzinfo=timezone.utc),
        "payload_digest": "sha256:abc",
    }
    values[field] = value
    with pytest.raises(ValueError, match="^market event identity fields must be non-empty$"):
        MarketEvent(**values)


@pytest.mark.parametrize("field", ["event_time", "received_at"])
def test_market_event_rejects_naive_temporal_values(field: str) -> None:
    values: dict[str, Any] = {
        "source_event_id": "evt-1",
        "source": "provider",
        "symbol": "BTCUSDT",
        "event_time": datetime(2026, 9, 24, 9, tzinfo=timezone.utc),
        "received_at": datetime(2026, 9, 24, 9, 1, tzinfo=timezone.utc),
        "payload_digest": "sha256:abc",
    }
    values[field] = datetime(2026, 9, 24, 9)
    with pytest.raises(ValueError, match=f"^{field} must be timezone-aware UTC$"):
        MarketEvent(**values)


def test_market_event_rejects_blank_payload_digest() -> None:
    values: dict[str, Any] = {
        "source_event_id": "evt-1",
        "source": "provider",
        "symbol": "BTCUSDT",
        "event_time": datetime(2026, 9, 24, 9, tzinfo=timezone.utc),
        "received_at": datetime(2026, 9, 24, 9, 1, tzinfo=timezone.utc),
        "payload_digest": "",
    }
    with pytest.raises(ValueError, match="^payload_digest must be non-empty$"):
        MarketEvent(**values)


def test_market_event_rejects_non_utc_aware_offset() -> None:
    from datetime import timedelta

    offset = timezone(timedelta(hours=4))
    with pytest.raises(ValueError, match="UTC"):
        MarketEvent(
            "evt-1",
            "provider",
            "BTCUSDT",
            datetime(2026, 9, 24, 13, tzinfo=offset),
            datetime(2026, 9, 24, 9, 1, tzinfo=timezone.utc),
            "sha256:abc",
        )
