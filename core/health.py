"""FILE: core/health.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.1
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Own the authoritative runtime health state and safe lifecycle transitions.
LAYER: core
OWNS: Runtime health state, lifecycle state transitions, and immutable health snapshots.
DOES_NOT_OWN: provider acquisition, analysis business logic, Telegram transport, persistence, decision, risk.
DEPENDENCIES: stdlib:dataclasses; stdlib:datetime; stdlib:enum
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum


class RuntimeState(StrEnum):
    RUNNING = "running"
    DEGRADED = "degraded"
    STOPPED = "stopped"
    FAILED = "failed"


class ActivityState(StrEnum):
    IDLE = "idle"
    SCANNING = "scanning"
    ANALYZING = "analyzing"


@dataclass(frozen=True, slots=True)
class HealthSnapshot:
    runtime: RuntimeState
    activity: ActivityState
    provider_healthy: int
    provider_total: int
    queue_depth: int
    active_tasks: int
    last_event_at: datetime | None
    last_analysis_at: datetime | None
    clock_ok: bool
    data_flow_ok: bool
    errors: int
    observed_at: datetime

    def __post_init__(self) -> None:
        if self.provider_healthy < 0 or self.provider_total < 0:
            raise ValueError("provider counts must be non-negative")
        if self.provider_healthy > self.provider_total:
            raise ValueError("healthy providers cannot exceed total providers")
        if self.queue_depth < 0 or self.active_tasks < 0 or self.errors < 0:
            raise ValueError("health counters must be non-negative")
        for name, value in (
            ("last_event_at", self.last_event_at),
            ("last_analysis_at", self.last_analysis_at),
            ("observed_at", self.observed_at),
        ):
            if value is not None and (
                value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value)
            ):
                raise ValueError(f"{name} must be timezone-aware UTC")


class RuntimeHealth:
    """Single authoritative in-memory runtime health state."""

    def __init__(self, *, observed_at: datetime) -> None:
        self._snapshot = HealthSnapshot(
            runtime=RuntimeState.RUNNING,
            activity=ActivityState.IDLE,
            provider_healthy=0,
            provider_total=0,
            queue_depth=0,
            active_tasks=0,
            last_event_at=None,
            last_analysis_at=None,
            clock_ok=True,
            data_flow_ok=True,
            errors=0,
            observed_at=self._require_utc(observed_at),
        )

    def snapshot(self) -> HealthSnapshot:
        return self._snapshot

    def update(self, **changes: object) -> HealthSnapshot:
        allowed = set(self._snapshot.__dataclass_fields__)
        unknown = set(changes) - allowed
        if unknown:
            raise ValueError(f"unknown health fields: {sorted(unknown)}")
        changes["observed_at"] = self._require_utc(
            changes.get("observed_at", datetime.now(timezone.utc))
        )
        current = {
            field: getattr(self._snapshot, field) for field in self._snapshot.__dataclass_fields__
        }
        self._snapshot = HealthSnapshot(**{**current, **changes})
        return self._snapshot

    @staticmethod
    def _require_utc(value: object) -> datetime:
        if (
            not isinstance(value, datetime)
            or value.tzinfo is None
            or value.utcoffset() != timezone.utc.utcoffset(value)
        ):
            raise ValueError("observed_at must be timezone-aware UTC")
        return value
