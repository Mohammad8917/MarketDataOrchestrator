"""Integration coverage for the strategy backtest to metrics flow."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID, uuid5

from backtest.strategy_engine import StrategyBacktestEngine
from domain.common.timeframe import Timeframe
from domain.market_data_event import MarketDataEvent
from strategy.evaluation.performance_metrics import calculate_performance_metrics
from strategy.trend.donchian import DonchianStrategy


def event(index: int, close: str) -> MarketDataEvent:
    timestamp = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(hours=index)
    price = Decimal(close)
    return MarketDataEvent(
        event_id=uuid5(UUID("00000000-0000-0000-0000-000000000001"), str(index)),
        provider="test",
        symbol="BTCUSDT",
        timeframe=Timeframe.parse("1h"),
        event_time=timestamp,
        received_at=timestamp,
        open=price,
        high=price,
        low=price,
        close=price,
        volume=Decimal("1"),
    )


def test_strategy_backtest_output_is_consumed_by_performance_metrics() -> None:
    events = (
        event(0, "100"),
        event(1, "101"),
        event(2, "103"),
        event(3, "102"),
    )

    equity_curve = StrategyBacktestEngine(initial_capital=Decimal("100")).run(
        events,
        DonchianStrategy(period=2),
    )

    metrics = calculate_performance_metrics(equity_curve)

    assert metrics.observations == len(equity_curve)
    assert metrics.initial_equity == equity_curve.equity[0]
    assert metrics.final_equity == equity_curve.equity[-1]
    assert metrics.max_drawdown <= Decimal("0")
