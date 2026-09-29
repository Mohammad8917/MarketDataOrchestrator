"""FILE: tests/backtest/test_historical_clock.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-29
DATE_PERSIAN: 1405-07-07
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify strict historical event ordering for strategy backtest execution.
LAYER: tests
OWNS: Historical clock ordering assertions.
DOES_NOT_OWN: Production execution policy.
DEPENDENCIES: datetime, decimal, backtest.strategy_engine, domain.common.timeframe, domain.market_data_event, strategy.trend.donchian, pytest
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import pytest
from backtest.strategy_engine import StrategyBacktestEngine
from domain.common.timeframe import Timeframe
from domain.market_data_event import MarketDataEvent
from strategy.trend.donchian import DonchianStrategy

def event(index: int) -> MarketDataEvent:
    t=datetime(2026,1,1,tzinfo=timezone.utc)+timedelta(minutes=index)
    return MarketDataEvent.create(provider="test",symbol="BTCUSDT",timeframe=Timeframe.parse("1m"),event_time=t,received_at=t,open=Decimal("10"),high=Decimal("11"),low=Decimal("9"),close=Decimal("10"),volume=Decimal("1"))

def test_rejects_non_increasing_historical_clock() -> None:
    first, second = event(0), event(1)
    with pytest.raises(ValueError, match="strictly ordered"):
        StrategyBacktestEngine().run((second, first), DonchianStrategy(period=2))

def test_accepts_strictly_increasing_historical_clock() -> None:
    curve=StrategyBacktestEngine().run((event(0),event(1)),DonchianStrategy(period=2))
    assert len(curve)==2
