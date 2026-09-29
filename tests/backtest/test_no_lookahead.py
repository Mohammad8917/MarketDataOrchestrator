"""FILE: tests/backtest/test_no_lookahead.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-29
DATE_PERSIAN: 1405-07-07
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify that strategy decisions use only prior bars and execute on the next bar.
LAYER: tests
OWNS: No-lookahead regression assertions.
DOES_NOT_OWN: Production strategy policy.
DEPENDENCIES: datetime, decimal, backtest.strategy_engine, domain.common.timeframe, domain.market_data_event, strategy.trend.donchian
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from backtest.strategy_engine import StrategyBacktestEngine
from domain.common.timeframe import Timeframe
from domain.market_data_event import MarketDataEvent
from strategy.trend.donchian import DonchianStrategy

def event(index:int,high:int,low:int,close:int)->MarketDataEvent:
    t=datetime(2026,1,1,tzinfo=timezone.utc)+timedelta(minutes=index)
    return MarketDataEvent.create(provider="test",symbol="BTCUSDT",timeframe=Timeframe.parse("1m"),event_time=t,received_at=t,open=Decimal("10"),high=Decimal(str(high)),low=Decimal(str(low)),close=Decimal(str(close)),volume=Decimal("1"))

def test_breakout_signal_cannot_profit_from_same_bar_close() -> None:
    events=(event(0,10,8,9),event(1,11,8,10),event(2,13,9,13))
    curve=StrategyBacktestEngine(Decimal("1000")).run(events,DonchianStrategy(period=2))
    assert curve.equity==(Decimal("1000"),Decimal("1000"),Decimal("1000"))

def test_breakout_signal_is_applied_to_following_bar() -> None:
    events=(event(0,10,8,9),event(1,11,8,10),event(2,12,9,13),event(3,14,10,14))
    curve=StrategyBacktestEngine(Decimal("1000")).run(events,DonchianStrategy(period=2))
    assert curve.equity[-1]==Decimal("1000")*Decimal("14")/Decimal("13")
