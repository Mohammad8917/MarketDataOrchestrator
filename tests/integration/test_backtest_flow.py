"""FILE: tests/integration/test_backtest_flow.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-25
DATE_PERSIAN: 1405-07-03
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify the minimal persisted-data-to-equity-curve backtest vertical slice.
LAYER: tests
OWNS: End-to-end assertions for MarketDataStore and BacktestEngine integration.
DOES_NOT_OWN: production persistence behavior, backtest policy beyond the minimal contract, external providers
DEPENDENCIES: datetime, decimal, domain.common.timeframe, domain.market_data_event, persistence.market_data_store, backtest.engine, shared.contracts.equity_curve
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from backtest.engine import SimpleBacktestEngine
from domain.common.timeframe import Timeframe
from domain.market_data_event import MarketDataEvent
import pytest

from persistence.market_data_store import MarketDataStore
from shared.contracts.equity_curve import EquityCurveData
from typing import cast


def make_event(hour: int, close: str) -> MarketDataEvent:
    return MarketDataEvent.create(
        provider="demo",
        symbol="BTCUSD",
        timeframe=Timeframe.parse("1h"),
        event_time=datetime(2026, 9, 24, hour, tzinfo=timezone.utc),
        received_at=datetime(2026, 9, 24, hour, 1, tzinfo=timezone.utc),
        open=Decimal(close),
        high=Decimal(close),
        low=Decimal(close),
        close=Decimal(close),
        volume=Decimal("1"),
    )


def test_market_data_store_to_backtest_equity_curve(tmp_path) -> None:
    events = (make_event(12, "100"), make_event(13, "110"), make_event(14, "105"))

    with MarketDataStore(tmp_path / "market.db") as store:
        for event in events:
            store.write(event)
        replayed = store.read_all()

    curve = SimpleBacktestEngine().run(replayed)

    assert isinstance(curve, EquityCurveData)
    assert curve.timestamps == tuple(event.event_time for event in events)
    assert curve.equity == (
        Decimal("100"),
        Decimal("110"),
        Decimal("105"),
    )
    assert curve.drawdown == (
        Decimal("0"),
        Decimal("0"),
        Decimal("-0.0454545454545454545454545455"),
    )


def test_equity_curve_invariants() -> None:
    timestamp = datetime(2026, 9, 24, 12, tzinfo=timezone.utc)
    timestamps: tuple[datetime, ...] = (timestamp,)
    equity: tuple[Decimal, ...] = (Decimal("100"),)
    drawdown: tuple[Decimal, ...] = (Decimal("0"),)

    with pytest.raises(ValueError, match="equal length"):
        EquityCurveData(timestamps=timestamps, equity=(), drawdown=drawdown)

    with pytest.raises(ValueError, match="timezone-aware"):
        EquityCurveData(
            timestamps=(datetime(2026, 9, 24, 12),),
            equity=equity,
            drawdown=drawdown,
        )

    with pytest.raises(ValueError, match="UTC"):
        EquityCurveData(
            timestamps=(datetime(2026, 9, 24, 12, tzinfo=timezone(timedelta(hours=1))),),
            equity=equity,
            drawdown=drawdown,
        )

    with pytest.raises(ValueError, match="finite Decimal"):
        EquityCurveData(
            timestamps=timestamps,
            equity=(cast(Decimal, object()),),
            drawdown=drawdown,
        )

    with pytest.raises(ValueError, match="finite Decimal"):
        EquityCurveData(
            timestamps=timestamps,
            equity=(Decimal("NaN"),),
            drawdown=drawdown,
        )

    with pytest.raises(ValueError, match="positive"):
        EquityCurveData(
            timestamps=timestamps,
            equity=(Decimal("0"),),
            drawdown=drawdown,
        )

    with pytest.raises(ValueError, match="finite Decimal"):
        EquityCurveData(
            timestamps=timestamps,
            equity=equity,
            drawdown=(cast(Decimal, object()),),
        )

    with pytest.raises(ValueError, match="finite Decimal"):
        EquityCurveData(
            timestamps=timestamps,
            equity=equity,
            drawdown=(Decimal("NaN"),),
        )

    with pytest.raises(ValueError, match="cannot be positive"):
        EquityCurveData(
            timestamps=timestamps,
            equity=equity,
            drawdown=(Decimal("0.1"),),
        )

    later = timestamp + timedelta(hours=1)
    with pytest.raises(ValueError, match="ordered ascending"):
        EquityCurveData(
            timestamps=(later, timestamp),
            equity=(Decimal("100"), Decimal("101")),
            drawdown=(Decimal("0"), Decimal("0")),
        )

    with pytest.raises(ValueError, match="first drawdown must be zero"):
        EquityCurveData(
            timestamps=timestamps,
            equity=equity,
            drawdown=(Decimal("-0.1"),),
        )


def test_equity_curve_iteration_and_length() -> None:
    timestamp = datetime(2026, 9, 24, 12, tzinfo=timezone.utc)
    curve = EquityCurveData(
        timestamps=(timestamp,),
        equity=(Decimal("100"),),
        drawdown=(Decimal("0"),),
    )

    assert len(curve) == 1
    assert tuple(curve) == (Decimal("100"),)
