"""FILE: domain/common/timeframe.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Define immutable, validated market timeframe values used by domain logic.
LAYER: domain
OWNS: Timeframe value semantics, canonical interval parsing, positive duration invariants, and stable serialization of timeframe values.
DOES_NOT_OWN: provider-specific interval aliases, scheduling, data retrieval, candle aggregation, or higher-level strategy behavior.
DEPENDENCIES: datetime, re
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import re


_TIMEFRAME_PATTERN = re.compile(r"^(?P<value>[1-9][0-9]*)(?P<unit>[mhdw])$")


@dataclass(frozen=True, slots=True)
class Timeframe:
    """A canonical positive trading interval."""

    value: int
    unit: str

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValueError("timeframe value must be positive")
        if self.unit not in {"m", "h", "d", "w"}:
            raise ValueError("timeframe unit must be one of: m, h, d, w")

    @classmethod
    def parse(cls, value: str) -> Timeframe:
        """Parse a canonical timeframe such as 5m or 1h."""
        if not isinstance(value, str):
            raise TypeError("timeframe must be a string")
        match = _TIMEFRAME_PATTERN.fullmatch(value)
        if match is None:
            raise ValueError("invalid timeframe; expected <positive integer><m|h|d|w>")
        return cls(int(match.group("value")), match.group("unit"))

    @property
    def code(self) -> str:
        """Return the canonical serialized representation."""
        return f"{self.value}{self.unit}"

    @property
    def duration(self) -> timedelta:
        """Return the exact duration represented by the timeframe."""
        units = {
            "m": timedelta(minutes=self.value),
            "h": timedelta(hours=self.value),
            "d": timedelta(days=self.value),
            "w": timedelta(weeks=self.value),
        }
        return units[self.unit]

    def __str__(self) -> str:
        return self.code
