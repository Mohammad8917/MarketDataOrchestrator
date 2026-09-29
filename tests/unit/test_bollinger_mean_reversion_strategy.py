"""FILE: tests/unit/test_bollinger_mean_reversion_strategy.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-29
DATE_PERSIAN: 1405-07-07
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify deterministic Bollinger-band mean-reversion positions over historical MarketBar values.
LAYER: tests
OWNS: Verification of the bollinger_mean_reversion_strategy test contract and behavior.
DOES_NOT_OWN: Production implementation, runtime orchestration, or release approval.
DEPENDENCIES: shared.contracts.market_bar; strategy.volatility.bollinger_mean_reversion; pytest
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from shared.contracts.market_bar import MarketBar
from strategy.volatility.bollinger_mean_reversion import (
    BollingerMeanReversionPosition,
    BollingerMeanReversionStrategy,
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
    with pytest.raises(ValueError, match="period must be greater than 1"):
        BollingerMeanReversionStrategy(period=1)
    with pytest.raises(ValueError, match="deviation multiplier"):
        BollingerMeanReversionStrategy(deviation_multiplier=Decimal("0"))
    with pytest.raises(ValueError, match="deviation multiplier"):
        BollingerMeanReversionStrategy(deviation_multiplier=Decimal("NaN"))


def test_warmup_is_flat_until_period_is_available() -> None:
    events = tuple(make_bar(i, value) for i, value in enumerate((10, 10, 10)))
    signals = BollingerMeanReversionStrategy(
        period=3,
        deviation_multiplier=Decimal("1"),
    ).signals(events)
    assert signals[:2] == (
        BollingerMeanReversionPosition.FLAT,
        BollingerMeanReversionPosition.FLAT,
    )
    assert signals[2] is BollingerMeanReversionPosition.LONG


def test_enters_long_at_or_below_lower_band() -> None:
    events = tuple(make_bar(i, value) for i, value in enumerate((10, 10, 10)))
    strategy = BollingerMeanReversionStrategy(
        period=3,
        deviation_multiplier=Decimal("1"),
    )
    assert strategy.signals(events)[-1] is BollingerMeanReversionPosition.LONG


def test_exits_long_when_price_reaches_mean() -> None:
    events = tuple(make_bar(i, value) for i, value in enumerate((10, 10, 10, 11)))
    strategy = BollingerMeanReversionStrategy(
        period=3,
        deviation_multiplier=Decimal("1"),
    )
    signals = strategy.signals(events)
    assert signals[2] is BollingerMeanReversionPosition.LONG
    assert signals[3] is BollingerMeanReversionPosition.FLAT


def test_strict_event_order_is_required() -> None:
    events = (make_bar(1, 10), make_bar(1, 9))
    with pytest.raises(ValueError, match="strictly ordered"):
        BollingerMeanReversionStrategy(period=3).signals(events)
