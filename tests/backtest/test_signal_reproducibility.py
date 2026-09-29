"""FILE: tests/backtest/test_signal_reproducibility.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-29
DATE_PERSIAN: 1405-07-07
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify deterministic repeated strategy signal generation.
LAYER: tests
OWNS: Signal reproducibility assertions.
DOES_NOT_OWN: Backtest accounting or persistence.
DEPENDENCIES: datetime, decimal, shared.contracts.market_bar, strategy.trend.donchian
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from shared.contracts.market_bar import MarketBar
from strategy.trend.donchian import DonchianStrategy

def bar(index:int,close:int)->MarketBar:
    return MarketBar(event_time=datetime(2026,1,1,tzinfo=timezone.utc)+timedelta(minutes=index),open=Decimal(str(close)),high=Decimal(str(close+1)),low=Decimal(str(close-1)),close=Decimal(str(close)),volume=Decimal("1"))

def test_same_historical_bars_produce_identical_signals() -> None:
    bars=tuple(bar(i,c) for i,c in enumerate((9,10,13,14,12)))
    strategy=DonchianStrategy(period=2)
    assert strategy.signals(bars)==strategy.signals(bars)
