"""FILE: shared/models/evidence.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Define the canonical immutable provenance metadata boundary shared by evidence-producing and evidence-consuming components.
LAYER: shared
OWNS: ProvenanceMetadata contract, field validation, UTC boundary semantics, and provenance identity invariants.
DOES_NOT_OWN: provider I/O, persistence mutation, final decision, risk, evidence scoring, or external calls.
DEPENDENCIES: stdlib:dataclasses; stdlib:datetime
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from dataclasses import dataclass
from datetime import datetime, timezone

PROVENANCE_CONTRACT_ID = "provenance_metadata"
PROVENANCE_CONTRACT_VERSION = "1.0.0"


def _require_utc(value: datetime, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
        raise ValueError(f"{field_name} must be timezone-aware UTC")


def _require_non_empty(value: str, field_name: str) -> None:
    if not value.strip():
        raise ValueError(f"{field_name} must not be empty")


@dataclass(frozen=True, slots=True)
class ProvenanceMetadata:
    """Immutable source traceability attached to externally derived evidence."""

    source_event_id: str
    source: str
    observed_at: datetime
    received_at: datetime
    content_digest: str
    contract_version: str = PROVENANCE_CONTRACT_VERSION

    def __post_init__(self) -> None:
        _require_non_empty(self.source_event_id, "source_event_id")
        _require_non_empty(self.source, "source")
        _require_non_empty(self.content_digest, "content_digest")
        _require_utc(self.observed_at, "observed_at")
        _require_utc(self.received_at, "received_at")
        if not self.contract_version:
            raise ValueError("contract_version must not be empty")


class ProvenanceProvider:
    """Marker interface for components exposing canonical provenance."""

    def provenance(self) -> ProvenanceMetadata:
        raise NotImplementedError
