from datetime import datetime
from decimal import Decimal
from typing import get_type_hints

from backtest.engine import BacktestEngine
from domain.market_data_event import MarketDataEvent
from shared.contracts.equity_curve import EquityCurve


def test_equity_curve_is_interface_only() -> None:
    assert getattr(EquityCurve, "_is_protocol", False) is True
    assert get_type_hints(getattr(EquityCurve.timestamps, "fget"))["return"] == tuple[datetime, ...]
    assert get_type_hints(getattr(EquityCurve.equity, "fget"))["return"] == tuple[Decimal, ...]
    assert get_type_hints(getattr(EquityCurve.drawdown, "fget"))["return"] == tuple[Decimal, ...]


def test_backtest_engine_run_signature_is_typed() -> None:
    assert getattr(BacktestEngine, "_is_protocol", False) is True
    hints = get_type_hints(BacktestEngine.run)
    assert hints["events"] == tuple[MarketDataEvent, ...]
    assert hints["return"] is EquityCurve
