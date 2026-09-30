from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from backtest.regime_analyzer import RegimeAnalysisReplay
from domain.common.timeframe import Timeframe
from domain.market_data_event import MarketDataEvent

NOW = datetime(2026, 9, 30, tzinfo=timezone.utc)


def make_events(count: int) -> tuple[MarketDataEvent, ...]:
    return tuple(
        MarketDataEvent.create(
            provider="test",
            symbol="BTCUSDT",
            timeframe=Timeframe.M1,
            event_time=NOW + timedelta(minutes=index),
            received_at=NOW + timedelta(minutes=index),
            open=Decimal(str(100 + index)),
            high=Decimal(str(101 + index)),
            low=Decimal(str(99 + index)),
            close=Decimal(str(100 + index)),
            volume=Decimal("1"),
        )
        for index in range(count)
    )


def test_replay_uses_only_history_available_at_each_event() -> None:
    events = make_events(6)
    result = RegimeAnalysisReplay(
        trend_lookback=4,
        volatility_short_lookback=2,
        volatility_long_lookback=4,
    ).run(events)

    assert len(result.results) == 3
    assert [item.event_time for item in result.results] == [
        NOW + timedelta(minutes=index) for index in (3, 4, 5)
    ]
    assert [item.source_event_id for item in result.results] == [
        str(event.event_id) for event in events[3:]
    ]


def test_replay_is_deterministic() -> None:
    events = make_events(6)
    replay = RegimeAnalysisReplay(
        trend_lookback=4,
        volatility_short_lookback=2,
        volatility_long_lookback=4,
    )
    assert replay.run(events) == replay.run(events)


def test_replay_rejects_unordered_events() -> None:
    events = make_events(6)
    with pytest.raises(ValueError, match="strictly ordered"):
        RegimeAnalysisReplay(
            trend_lookback=4,
            volatility_short_lookback=2,
            volatility_long_lookback=4,
        ).run((events[0], events[2], events[1], *events[3:]))


def test_replay_rejects_insufficient_history() -> None:
    with pytest.raises(ValueError, match="insufficient history"):
        RegimeAnalysisReplay(
            trend_lookback=4,
            volatility_short_lookback=2,
            volatility_long_lookback=4,
        ).run(make_events(3))
