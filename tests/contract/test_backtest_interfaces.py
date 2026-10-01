from datetime import datetime
from decimal import Decimal
from typing import get_type_hints

from backtest.engine import BacktestEngine
from domain.market_data_event import MarketDataEvent
from shared.contracts.equity_curve import EquityCurve


def _property_type(name: str) -> object:
    descriptor = EquityCurve.__dict__[name]
    return get_type_hints(descriptor.fget)["return"]


def test_equity_curve_is_interface_only() -> None:
    assert getattr(EquityCurve, "_is_protocol", False) is True
    assert _property_type("timestamps") == tuple[datetime, ...]
    assert _property_type("equity") == tuple[Decimal, ...]
    assert _property_type("drawdown") == tuple[Decimal, ...]


def test_backtest_engine_run_signature_is_typed() -> None:
    assert getattr(BacktestEngine, "_is_protocol", False) is True
    hints = get_type_hints(BacktestEngine.run)
    assert hints["events"] == tuple[MarketDataEvent, ...]
    assert hints["return"] is EquityCurve
