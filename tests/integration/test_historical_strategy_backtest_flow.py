"""FILE: tests/integration/test_historical_strategy_backtest_flow.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-29
DATE_PERSIAN: 1405-07-07
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify persisted MarketDataEvent replay through Donchian strategy execution into EquityCurve.
LAYER: tests
OWNS: End-to-end assertions for persistence, historical strategy, backtest execution, and equity-curve output.
DOES_NOT_OWN: Production persistence behavior, strategy implementation, backtest policy, provider transport, or release approval.
DEPENDENCIES: datetime, decimal, backtest.strategy_engine, domain.common.timeframe, domain.market_data_event, persistence.market_data_store, strategy.trend.donchian, pytest
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from backtest.strategy_engine import StrategyBacktestEngine
from domain.common.timeframe import Timeframe
from domain.market_data_event import MarketDataEvent
from persistence.market_data_store import MarketDataStore
from strategy.trend.donchian import DonchianStrategy


def make_event(
    index: int,
    *,
    high: int,
    low: int,
    close: int,
) -> MarketDataEvent:
    timestamp = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=index)
    return MarketDataEvent.create(
        provider="test",
        symbol="BTCUSDT",
        timeframe=Timeframe.parse("1m"),
        event_time=timestamp,
        received_at=timestamp,
        open=Decimal("10"),
        high=Decimal(str(high)),
        low=Decimal(str(low)),
        close=Decimal(str(close)),
        volume=Decimal("1"),
    )


def test_persisted_events_execute_through_donchian_into_equity_curve(tmp_path) -> None:
    events = (
        make_event(0, high=10, low=8, close=9),
        make_event(1, high=11, low=8, close=10),
        make_event(2, high=12, low=9, close=13),
        make_event(3, high=14, low=10, close=14),
    )

    with MarketDataStore(tmp_path / "market.db") as store:
        for event in events:
            store.write(event)
        replayed = store.read_all()

    curve = StrategyBacktestEngine(Decimal("1000")).run(
        replayed,
        DonchianStrategy(period=2),
    )

    assert curve.timestamps == tuple(event.event_time for event in events)
    assert curve.equity == (
        Decimal("1000"),
        Decimal("1000"),
        Decimal("1000"),
        Decimal("1000") * Decimal("14") / Decimal("13"),
    )
