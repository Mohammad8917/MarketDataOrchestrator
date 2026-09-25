"""FILE: tests/unit/test_market_runtime.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-25
DATE_PERSIAN: 1405-07-03
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify market runtime activation and lifecycle state behavior.
LAYER: tests
OWNS: Unit coverage for MarketRuntime.
DOES_NOT_OWN: Production runtime policy, Telegram transport, market-data acquisition
DEPENDENCIES: app
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

import pytest

from app.market_runtime import Market, MarketRuntime, MarketStatus


def test_default_runtime_enables_only_crypto() -> None:
    runtime = MarketRuntime()

    assert runtime.state(Market.CRYPTO).status is MarketStatus.IDLE
    assert runtime.state(Market.FOREX).status is MarketStatus.DISABLED
    assert runtime.state(Market.GOLD).status is MarketStatus.DISABLED


def test_market_can_be_enabled_and_disabled() -> None:
    runtime = MarketRuntime(frozenset())

    enabled = runtime.set_enabled(Market.FOREX, True)
    assert enabled.enabled is True
    assert enabled.status is MarketStatus.IDLE

    disabled = runtime.set_enabled(Market.FOREX, False)
    assert disabled.enabled is False
    assert disabled.status is MarketStatus.DISABLED


def test_scan_and_analysis_lifecycle() -> None:
    runtime = MarketRuntime()

    assert runtime.start_scan(Market.CRYPTO).status is MarketStatus.SCANNING
    assert runtime.start_analysis(Market.CRYPTO).status is MarketStatus.ANALYZING
    assert runtime.finish_activity(Market.CRYPTO).status is MarketStatus.IDLE


def test_disabled_market_cannot_start_activity() -> None:
    runtime = MarketRuntime(frozenset())

    with pytest.raises(RuntimeError, match="forex market is disabled"):
        runtime.start_scan(Market.FOREX)


def test_states_returns_all_supported_markets() -> None:
    runtime = MarketRuntime(frozenset({Market.GOLD}))

    assert tuple(state.market for state in runtime.states()) == (
        Market.CRYPTO,
        Market.FOREX,
        Market.GOLD,
    )


def test_rejects_unsupported_enabled_market() -> None:
    with pytest.raises(ValueError, match="unsupported market"):
        MarketRuntime(frozenset({"crypto"}))  # type: ignore[arg-type]
