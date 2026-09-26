from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

from backtest.engine import SimpleBacktestEngine
from domain.common.timeframe import Timeframe
from domain.market_data_event import MarketDataEvent


def make_events(count: int) -> tuple[MarketDataEvent, ...]:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    timeframe = Timeframe.parse("1m")
    return tuple(
        MarketDataEvent.create(
            provider="benchmark",
            symbol="BTC/USDT",
            timeframe=timeframe,
            event_time=start + timedelta(minutes=index),
            received_at=start + timedelta(minutes=index, seconds=1),
            open=Decimal("100"),
            high=Decimal("101"),
            low=Decimal("99"),
            close=Decimal(100 + (index % 20)),
            volume=Decimal("1"),
        )
        for index in range(count)
    )


def test_simple_backtest_engine_throughput(benchmark: Any) -> None:
    events = make_events(4_096)
    engine = SimpleBacktestEngine()

    curve = benchmark(engine.run, events)

    assert len(curve.timestamps) == len(events)
    assert len(curve.equity) == len(events)
    assert len(curve.drawdown) == len(events)
