"""FILE: tests/backtest/test_strategy_protocol.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-29
DATE_PERSIAN: 1405-07-07
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify the consumer-owned historical strategy protocol and Donchian compatibility.
LAYER: tests
OWNS: Verification of the test_strategy_protocol test contract and behavior.
DOES_NOT_OWN: Production implementation, runtime orchestration, or release approval.
DEPENDENCIES: backtest.strategy; shared.contracts.market_bar; strategy.trend.donchian
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timezone
from decimal import Decimal

from backtest.strategy import HistoricalStrategy, PositionSignal
from shared.contracts.market_bar import MarketBar
from strategy.trend.donchian import DonchianPosition, DonchianStrategy


def make_bar(index: int) -> MarketBar:
    return MarketBar(
        event_time=datetime(2026, 1, 1, tzinfo=timezone.utc).replace(minute=index),
        open=Decimal("10"),
        high=Decimal("12"),
        low=Decimal("8"),
        close=Decimal("11"),
        volume=Decimal("1"),
    )


def test_donchian_satisfies_historical_strategy_protocol() -> None:
    assert isinstance(DonchianStrategy(period=2), HistoricalStrategy)


def test_donchian_position_satisfies_position_signal_protocol() -> None:
    assert isinstance(DonchianPosition.LONG, PositionSignal)


def test_protocol_returns_position_signals() -> None:
    result = DonchianStrategy(period=2).signals((make_bar(0), make_bar(1)))
    assert all(isinstance(position, PositionSignal) for position in result)
