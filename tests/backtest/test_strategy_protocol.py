"""Tests for the consumer-owned historical strategy protocol."""

from datetime import datetime, timezone
from decimal import Decimal

from backtest.strategy import BacktestPosition, HistoricalStrategy
from shared.contracts.market_bar import MarketBar
from strategy.trend.donchian import DonchianStrategy


def make_bar() -> MarketBar:
    return MarketBar(
        event_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
        open=Decimal("10"),
        high=Decimal("12"),
        low=Decimal("8"),
        close=Decimal("11"),
        volume=Decimal("1"),
    )


def test_donchian_satisfies_historical_strategy_protocol() -> None:
    assert isinstance(DonchianStrategy(period=2), HistoricalStrategy)


def test_protocol_returns_execution_neutral_position() -> None:
    result = DonchianStrategy(period=2).signals((make_bar(), make_bar(). __class__(
        event_time=datetime(2026, 1, 1, 0, 1, tzinfo=timezone.utc),
        open=Decimal("10"),
        high=Decimal("12"),
        low=Decimal("8"),
        close=Decimal("11"),
        volume=Decimal("1"),
    )))
    assert all(isinstance(position, BacktestPosition) for position in result)
