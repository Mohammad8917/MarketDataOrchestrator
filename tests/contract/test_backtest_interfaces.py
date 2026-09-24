"""FILE: tests/contract/test_backtest_interfaces.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-25
RESPONSIBILITY: Verify the typed terminal output and BacktestEngine interface contracts.
LAYER: tests
OWNS: Interface contract shape assertions.
DOES_NOT_OWN: BacktestEngine execution, EquityCurve implementation, runtime behavior
DEPENDENCIES: typing, domain.market_data_event, shared.contracts.equity_curve, backtest.engine
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import get_type_hints

from backtest.engine import BacktestEngine
from domain.market_data_event import MarketDataEvent
from shared.contracts.equity_curve import EquityCurve


def test_equity_curve_is_interface_only() -> None:
    assert getattr(EquityCurve, "_is_protocol", False) is True
    hints = get_type_hints(EquityCurve)
    assert hints["timestamps"] == tuple[datetime, ...]
    assert hints["equity"] == tuple[Decimal, ...]
    assert hints["drawdown"] == tuple[Decimal, ...]


def test_backtest_engine_run_signature_is_typed() -> None:
    assert getattr(BacktestEngine, "_is_protocol", False) is True
    hints = get_type_hints(BacktestEngine.run)
    assert hints["events"] == tuple[MarketDataEvent, ...]
    assert hints["return"] is EquityCurve
