"""FILE: tests/unit/test_rsi_mean_reversion_strategy.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-29
DATE_PERSIAN: 1405-07-07
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify deterministic RSI mean-reversion positions over historical MarketBar values.
LAYER: tests
OWNS: Verification of the rsi_mean_reversion_strategy test contract and behavior.
DOES_NOT_OWN: Production implementation, runtime orchestration, or release approval.
DEPENDENCIES: shared.contracts.market_bar; strategy.momentum.rsi_mean_reversion; pytest
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from shared.contracts.market_bar import MarketBar
from strategy.momentum.rsi_mean_reversion import (
    RsiMeanReversionPosition,
    RsiMeanReversionStrategy,
)


def make_bar(index: int, close: int) -> MarketBar:
    value = Decimal(str(close))
    return MarketBar(
        event_time=datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=index),
        open=value,
        high=value,
        low=value,
        close=value,
        volume=Decimal("1"),
    )


def test_parameters_must_be_valid() -> None:
    with pytest.raises(ValueError, match="period must be positive"):
        RsiMeanReversionStrategy(period=0)
    with pytest.raises(ValueError, match="oversold must be between 0 and 100"):
        RsiMeanReversionStrategy(oversold=Decimal("-1"))
    with pytest.raises(ValueError, match="overbought must be between 0 and 100"):
        RsiMeanReversionStrategy(overbought=Decimal("101"))
    with pytest.raises(ValueError, match="oversold must be less than overbought"):
        RsiMeanReversionStrategy(oversold=Decimal("70"), overbought=Decimal("70"))


def test_warmup_is_flat_until_period_is_available() -> None:
    events = tuple(make_bar(i, value) for i, value in enumerate((10, 9, 8, 7)))
    signals = RsiMeanReversionStrategy(period=3).signals(events)
    assert signals[:3] == (
        RsiMeanReversionPosition.FLAT,
        RsiMeanReversionPosition.FLAT,
        RsiMeanReversionPosition.FLAT,
    )
    assert signals[3] is RsiMeanReversionPosition.LONG


def test_enters_long_when_rsi_reaches_oversold() -> None:
    events = tuple(make_bar(i, value) for i, value in enumerate((10, 9, 8, 7)))
    assert RsiMeanReversionStrategy(period=3).signals(events)[-1] is (
        RsiMeanReversionPosition.LONG
    )


def test_exits_long_when_rsi_reaches_overbought() -> None:
    events = tuple(make_bar(i, value) for i, value in enumerate((10, 9, 8, 7, 8, 9, 10)))
    signals = RsiMeanReversionStrategy(period=3).signals(events)
    assert signals[3] is RsiMeanReversionPosition.LONG
    assert signals[-1] is RsiMeanReversionPosition.FLAT


def test_strict_event_order_is_required() -> None:
    events = (make_bar(1, 10), make_bar(1, 9))
    with pytest.raises(ValueError, match="strictly ordered"):
        RsiMeanReversionStrategy(period=3).signals(events)
