"""FILE: app/market_runtime.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-09-25
DATE_PERSIAN: 1405-07-03
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Own runtime activation and lifecycle state for the supported markets.
LAYER: app
OWNS: Market identity, enabled state, and scan/analysis lifecycle state.
DOES_NOT_OWN: Telegram transport, market-data acquisition, strategy logic, persistence policy, analysis implementation
DEPENDENCIES: None declared in current implementation.
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Market(str, Enum):
    CRYPTO = "crypto"
    FOREX = "forex"
    GOLD = "gold"


class MarketStatus(str, Enum):
    DISABLED = "disabled"
    IDLE = "idle"
    SCANNING = "scanning"
    ANALYZING = "analyzing"


@dataclass(frozen=True, slots=True)
class MarketRuntimeState:
    market: Market
    enabled: bool
    status: MarketStatus


class MarketRuntime:
    """Manage in-memory runtime state for the supported markets."""

    def __init__(self, enabled_markets: frozenset[Market] | None = None) -> None:
        enabled = enabled_markets if enabled_markets is not None else frozenset({Market.CRYPTO})
        if not enabled.issubset(set(Market)):
            raise ValueError("enabled_markets contains an unsupported market")
        self._enabled = set(enabled)
        self._status = {market: MarketStatus.IDLE if market in enabled else MarketStatus.DISABLED for market in Market}

    def set_enabled(self, market: Market, enabled: bool) -> MarketRuntimeState:
        self._validate_market(market)
        if enabled:
            self._enabled.add(market)
            self._status[market] = MarketStatus.IDLE
        else:
            self._enabled.discard(market)
            self._status[market] = MarketStatus.DISABLED
        return self.state(market)

    def state(self, market: Market) -> MarketRuntimeState:
        self._validate_market(market)
        return MarketRuntimeState(market, market in self._enabled, self._status[market])

    def states(self) -> tuple[MarketRuntimeState, ...]:
        return tuple(self.state(market) for market in Market)

    def start_scan(self, market: Market) -> MarketRuntimeState:
        self._require_enabled(market)
        self._status[market] = MarketStatus.SCANNING
        return self.state(market)

    def start_analysis(self, market: Market) -> MarketRuntimeState:
        self._require_enabled(market)
        self._status[market] = MarketStatus.ANALYZING
        return self.state(market)

    def finish_activity(self, market: Market) -> MarketRuntimeState:
        self._require_enabled(market)
        self._status[market] = MarketStatus.IDLE
        return self.state(market)

    @staticmethod
    def _validate_market(market: Market) -> None:
        if not isinstance(market, Market):
            raise TypeError("market must be a Market")

    def _require_enabled(self, market: Market) -> None:
        self._validate_market(market)
        if market not in self._enabled:
            raise RuntimeError(f"{market.value} market is disabled")
