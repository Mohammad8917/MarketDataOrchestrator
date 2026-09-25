"""FILE: validation/temporal_validator.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Validate temporal boundary semantics for explicit UTC timestamps and monotonic elapsed durations.
LAYER: validation
OWNS: Temporal validation rules, clock-skew assessment, and elapsed-duration validation.
DOES_NOT_OWN: provider business logic, timestamp fabrication, persistence mutation, or output formatting.
DEPENDENCIES: stdlib:datetime; stdlib:typing
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timedelta, timezone
from typing import Final

DEFAULT_MAX_CLOCK_SKEW: Final[timedelta] = timedelta(seconds=5)


def require_utc(value: datetime, field_name: str = "timestamp") -> None:
    if value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
        raise ValueError(f"{field_name} must be timezone-aware UTC")


def validate_event_boundary(event_time: datetime, received_at: datetime) -> None:
    require_utc(event_time, "event_time")
    require_utc(received_at, "received_at")
    if event_time > received_at:
        raise ValueError("event_time must not be later than received_at")


def assess_clock_skew(
    provider_time: datetime, local_time: datetime, max_skew: timedelta = DEFAULT_MAX_CLOCK_SKEW
) -> timedelta:
    require_utc(provider_time, "provider_time")
    require_utc(local_time, "local_time")
    if max_skew < timedelta(0):
        raise ValueError("max_skew must not be negative")
    skew = abs(local_time - provider_time)
    if skew > max_skew:
        raise ValueError(f"clock skew exceeds allowed threshold: {skew}")
    return skew


def validate_elapsed_duration(start: float, end: float) -> float:
    if start < 0 or end < 0:
        raise ValueError("monotonic readings must not be negative")
    if end < start:
        raise ValueError("monotonic end must not precede start")
    return end - start
