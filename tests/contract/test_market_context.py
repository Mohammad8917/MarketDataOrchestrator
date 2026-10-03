"""Adversarial runtime tests for the market-context contract boundary."""

from datetime import datetime, timezone

import pytest

from shared.contracts.market_context import (
    MARKET_CONTEXT_CONTRACT_VERSION,
    MarketContext,
)


def _context(**overrides: object) -> MarketContext:
    values: dict[str, object] = {
        "market": "Crypto",
        "symbol": "BTCUSDT",
        "timeframe": "1h",
        "event_time": datetime(2026, 10, 3, tzinfo=timezone.utc),
        "source_event_id": "event-1",
    }
    values.update(overrides)
    return MarketContext(**values)  # type: ignore[arg-type]


def test_accepts_current_contract_version() -> None:
    context = _context(contract_version=MARKET_CONTEXT_CONTRACT_VERSION)
    assert context.contract_version == MARKET_CONTEXT_CONTRACT_VERSION


@pytest.mark.parametrize("version", ["2.0.0", "1.0", "unknown"])
def test_rejects_unsupported_contract_versions(version: str) -> None:
    with pytest.raises(ValueError, match="unsupported contract_version"):
        _context(contract_version=version)


@pytest.mark.parametrize("version", ["", " "])
def test_rejects_blank_contract_versions(version: str) -> None:
    with pytest.raises(ValueError, match="contract_version must not be empty"):
        _context(contract_version=version)


@pytest.mark.parametrize("version", [None, 0, object()])
def test_rejects_non_string_contract_versions(version: object) -> None:
    with pytest.raises(ValueError, match="contract_version must be a string"):
        _context(contract_version=version)
