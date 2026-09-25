"""FILE: indicators/core/registry.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Resolve canonical indicator names to concrete implementations without provider or strategy coupling.
LAYER: indicators
OWNS: Indicator name normalization, registration, lookup, and default implementation mapping.
DOES_NOT_OWN: indicator algorithms, strategy execution, data ingestion, persistence, decision, risk, provider I/O
DEPENDENCIES: indicators.momentum.macd; indicators.momentum.rsi; indicators.trend.ema; indicators.trend.sma; indicators.volatility.atr; indicators.volatility.bollinger_bands; indicators.volatility.donchian_channels
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, ClassVar

from indicators.momentum.macd import MovingAverageConvergenceDivergence
from indicators.momentum.rsi import RelativeStrengthIndex
from indicators.trend.ema import ExponentialMovingAverage
from indicators.trend.sma import SimpleMovingAverage
from indicators.volatility.atr import AverageTrueRange
from indicators.volatility.bollinger_bands import BollingerBands
from indicators.volatility.donchian_channels import DonchianChannels

IndicatorFactory = Callable[..., Any]


class IndicatorRegistry:
    """Name-to-implementation registry for concrete indicator constructors."""

    _defaults: ClassVar[dict[str, IndicatorFactory]] = {
        "SMA": SimpleMovingAverage,
        "EMA": ExponentialMovingAverage,
        "RSI": RelativeStrengthIndex,
        "ATR": AverageTrueRange,
        "MACD": MovingAverageConvergenceDivergence,
        "DONCHIAN": DonchianChannels,
        "BOLLINGER": BollingerBands,
    }

    def __init__(self) -> None:
        self._factories = dict(self._defaults)

    def register(self, name: str, implementation: IndicatorFactory) -> None:
        normalized = self._normalize(name)
        if not callable(implementation):
            raise TypeError("implementation must be callable")
        self._factories[normalized] = implementation

    def get(self, name: str, *args: Any, **kwargs: Any) -> Any:
        normalized = self._normalize(name)
        try:
            implementation = self._factories[normalized]
        except KeyError as exc:
            raise KeyError(f"unknown indicator: {normalized}") from exc
        return implementation(*args, **kwargs)

    @staticmethod
    def _normalize(name: str) -> str:
        normalized = name.strip().upper()
        if not normalized:
            raise ValueError("indicator name must be non-empty")
        return normalized
