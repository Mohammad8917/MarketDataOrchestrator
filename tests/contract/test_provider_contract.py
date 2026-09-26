from dataclasses import FrozenInstanceError
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Any, cast

import pytest

from domain.common.timeframe import Timeframe
from domain.market_data_event import MarketDataEvent
from ingestion.interfaces.market_provider import MarketDataProvider


class ContractProvider:
    provider_id = "contract-provider"

    async def fetch(self, symbol: str, *, start: datetime, end: datetime) -> tuple[MarketDataEvent, ...]:
        return ()


class InvalidContractProvider:
    async def fetch(self, symbol: str, *, start: datetime, end: datetime) -> tuple[MarketDataEvent, ...]:
        return ()


def _event(**overrides: Any) -> MarketDataEvent:
    values: dict[str, Any] = {
        "provider": "provider", "symbol": "BTCUSDT", "timeframe": Timeframe.parse("1m"),
        "event_time": datetime(2026, 9, 24, 9, tzinfo=timezone.utc),
        "received_at": datetime(2026, 9, 24, 9, 1, tzinfo=timezone.utc),
        "open": Decimal("100"), "high": Decimal("110"), "low": Decimal("90"),
        "close": Decimal("105"), "volume": Decimal("12.5"),
    }
    values.update(overrides)
    return MarketDataEvent.create(**values)


def test_market_data_provider_is_runtime_protocol() -> None:
    assert isinstance(ContractProvider(), MarketDataProvider)


def test_invalid_provider_is_rejected_by_runtime_protocol() -> None:
    assert not isinstance(InvalidContractProvider(), MarketDataProvider)


def test_market_data_event_declares_frozen_dataclass() -> None:
    assert getattr(MarketDataEvent, "__dataclass_params__").frozen is True


def test_market_data_event_is_immutable_and_slotted() -> None:
    event = _event()
    with pytest.raises(FrozenInstanceError):
        cast(Any, event).symbol = "ETHUSDT"
    assert hasattr(event, "__slots__")
    assert not hasattr(event, "__dict__")


@pytest.mark.parametrize("field, value", [("provider", ""), ("symbol", "")])
def test_market_data_event_rejects_missing_identity(field: str, value: str) -> None:
    with pytest.raises(ValueError, match=f"^{field} must be a non-empty string$"):
        _event(**{field: value})


@pytest.mark.parametrize("field", ["event_time", "received_at"])
def test_market_data_event_rejects_naive_temporal_values(field: str) -> None:
    with pytest.raises(ValueError, match=f"^{field} must be timezone-aware$"):
        _event(**{field: datetime(2026, 9, 24, 9)})


def test_market_data_event_rejects_non_utc_aware_offset() -> None:
    offset = timezone(timedelta(hours=4))
    with pytest.raises(ValueError, match="^event_time must be UTC$"):
        _event(event_time=datetime(2026, 9, 24, 13, tzinfo=offset))


def test_market_data_event_rejects_received_at_before_event_time() -> None:
    with pytest.raises(ValueError, match="^received_at cannot precede event_time$"):
        _event(
            event_time=datetime(2026, 9, 24, 9, tzinfo=timezone.utc),
            received_at=datetime(2026, 9, 24, 8, 59, tzinfo=timezone.utc),
        )
