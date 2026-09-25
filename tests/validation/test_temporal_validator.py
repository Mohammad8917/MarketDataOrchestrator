"""FILE: tests/validation/test_temporal_validator.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify temporal validator UTC, ordering, skew, and monotonic-duration rules.
LAYER: tests
OWNS: Temporal validator verification.
DOES_NOT_OWN: production temporal policy.
DEPENDENCIES: stdlib:datetime; validation.temporal_validator
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timedelta, timezone
import pytest
from validation.temporal_validator import (
    assess_clock_skew,
    validate_elapsed_duration,
    validate_event_boundary,
)


def test_event_boundary_accepts_ordered_utc() -> None:
    t = datetime(2026, 9, 24, 8, tzinfo=timezone.utc)
    validate_event_boundary(t, t)


@pytest.mark.parametrize(
    "event_time,received_at",
    [
        (datetime(2026, 9, 24, 8), datetime(2026, 9, 24, 8, tzinfo=timezone.utc)),
        (datetime(2026, 9, 24, 8, tzinfo=timezone.utc), datetime(2026, 9, 24, 8)),
        (
            datetime(2026, 9, 24, 9, tzinfo=timezone.utc),
            datetime(2026, 9, 24, 8, tzinfo=timezone.utc),
        ),
    ],
)
def test_event_boundary_rejects_invalid(event_time: datetime, received_at: datetime) -> None:
    with pytest.raises(ValueError):
        validate_event_boundary(event_time, received_at)


def test_clock_skew() -> None:
    t = datetime(2026, 9, 24, 8, tzinfo=timezone.utc)
    assert assess_clock_skew(t, t + timedelta(seconds=2)) == timedelta(seconds=2)
    with pytest.raises(ValueError):
        assess_clock_skew(t, t + timedelta(seconds=6))
    with pytest.raises(ValueError):
        assess_clock_skew(t, t, timedelta(seconds=-1))


def test_elapsed_duration() -> None:
    assert validate_elapsed_duration(2.0, 5.5) == 3.5
    with pytest.raises(ValueError):
        validate_elapsed_duration(-1.0, 2.0)
    with pytest.raises(ValueError):
        validate_elapsed_duration(5.0, 2.0)
