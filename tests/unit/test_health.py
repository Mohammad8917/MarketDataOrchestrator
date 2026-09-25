"""FILE: tests/unit/test_health.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.1
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify authoritative runtime health state invariants and lifecycle observability.
LAYER: tests
OWNS: Health state unit verification.
DOES_NOT_OWN: Telegram presentation, provider transport, analysis execution.
DEPENDENCIES: stdlib:datetime; pytest; core.health
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timezone

import pytest

from core.health import ActivityState, RuntimeHealth, RuntimeState


def test_health_starts_running_and_idle() -> None:
    health = RuntimeHealth(observed_at=datetime(2026, 9, 24, 9, tzinfo=timezone.utc))
    snapshot = health.snapshot()
    assert snapshot.runtime is RuntimeState.RUNNING
    assert snapshot.activity is ActivityState.IDLE
    assert snapshot.clock_ok is True
    assert snapshot.data_flow_ok is True


def test_health_transitions_to_scanning_and_analyzing() -> None:
    health = RuntimeHealth(observed_at=datetime(2026, 9, 24, 9, tzinfo=timezone.utc))
    scanning = health.update(
        activity=ActivityState.SCANNING, active_tasks=4, provider_total=5, provider_healthy=5
    )
    assert scanning.activity is ActivityState.SCANNING
    assert scanning.active_tasks == 4
    analyzing = health.update(
        activity=ActivityState.ANALYZING,
        last_analysis_at=datetime(2026, 9, 24, 9, 1, tzinfo=timezone.utc),
    )
    assert analyzing.activity is ActivityState.ANALYZING
    assert analyzing.last_analysis_at is not None


def test_health_can_express_degraded_and_stopped_states() -> None:
    health = RuntimeHealth(observed_at=datetime(2026, 9, 24, 9, tzinfo=timezone.utc))
    degraded = health.update(runtime=RuntimeState.DEGRADED, clock_ok=False, errors=1)
    assert degraded.runtime is RuntimeState.DEGRADED
    assert degraded.clock_ok is False
    stopped = health.update(
        runtime=RuntimeState.STOPPED, activity=ActivityState.IDLE, active_tasks=0
    )
    assert stopped.runtime is RuntimeState.STOPPED


def test_health_rejects_invalid_counters_and_unknown_fields() -> None:
    health = RuntimeHealth(observed_at=datetime(2026, 9, 24, 9, tzinfo=timezone.utc))
    with pytest.raises(ValueError):
        health.update(provider_healthy=2, provider_total=1)
    with pytest.raises(ValueError):
        health.update(queue_depth=-1)
    with pytest.raises(ValueError, match="unknown"):
        health.update(not_a_health_field=True)


def test_health_rejects_non_utc_observed_time() -> None:
    with pytest.raises(ValueError):
        RuntimeHealth(observed_at=datetime(2026, 9, 24, 9))
