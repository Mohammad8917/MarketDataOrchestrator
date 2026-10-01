"""Contract tests for the provider-neutral market-data request boundary."""

from datetime import datetime, timedelta, timezone
from typing import Any, cast

import pytest

from domain.common.timeframe import Timeframe
from domain.market_data_request import CONTRACT_ID, CONTRACT_VERSION, MarketDataRequest
from domain.market_scope import MarketScope


def _request(**overrides: Any) -> MarketDataRequest:
    values: dict[str, Any] = {
        "market": MarketScope.CRYPTO,
        "symbol": "BTCUSDT",
        "timeframe": Timeframe.parse("1h"),
        "start": datetime(2026, 9, 24, 9, tzinfo=timezone.utc),
        "end": datetime(2026, 9, 24, 10, tzinfo=timezone.utc),
    }
    values.update(overrides)
    return MarketDataRequest(**values)


def test_request_declares_stable_contract_identity() -> None:
    assert CONTRACT_ID == "market_data_request_boundary"
    assert CONTRACT_VERSION == "1.0.0"
    assert _request().contract_version == CONTRACT_VERSION


def test_request_is_immutable_and_slotted() -> None:
    request = _request()
    with pytest.raises(AttributeError):
        cast(Any, request).symbol = "ETHUSDT"
    assert not hasattr(request, "__dict__")


def test_request_preserves_canonical_market_scope() -> None:
    for market in MarketScope:
        assert _request(market=market).market is market


@pytest.mark.parametrize("field", ["start", "end"])
def test_request_rejects_naive_datetime(field: str) -> None:
    with pytest.raises(ValueError, match=f"^{field} must be timezone-aware UTC$"):
        _request(**{field: datetime(2026, 9, 24, 9)})


def test_request_rejects_non_utc_offset() -> None:
    with pytest.raises(ValueError, match="^start must be timezone-aware UTC$"):
        _request(start=datetime(2026, 9, 24, 13, tzinfo=timezone(timedelta(hours=4))))


def test_request_rejects_invalid_window() -> None:
    start = datetime(2026, 9, 24, 10, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="^start must be before end$"):
        _request(start=start, end=start)


@pytest.mark.parametrize("field", ["symbol"])
def test_request_rejects_missing_identity(field: str) -> None:
    with pytest.raises(ValueError, match=f"^{field} must be a non-empty string$"):
        _request(**{field: ""})


def test_request_rejects_wrong_market_type() -> None:
    with pytest.raises(TypeError, match="^market must be MarketScope$"):
        _request(market="crypto")
