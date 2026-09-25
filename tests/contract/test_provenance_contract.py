"""FILE: tests/contract/test_provenance_contract.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify the provenance metadata contract invariants.
LAYER: tests
OWNS: Provenance contract verification.
DOES_NOT_OWN: production provenance behavior.
DEPENDENCIES: stdlib:datetime; shared.models.evidence
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from datetime import datetime, timezone
from typing import Any
import pytest
from shared.models.evidence import (
    PROVENANCE_CONTRACT_ID,
    PROVENANCE_CONTRACT_VERSION,
    ProvenanceMetadata,
    ProvenanceProvider,
)


def _metadata() -> ProvenanceMetadata:
    now = datetime(2026, 9, 24, 8, tzinfo=timezone.utc)
    return ProvenanceMetadata("evt-1", "provider:test", now, now, "sha256:abc")


def test_provenance_rejects_empty_contract_version() -> None:
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError, match="contract_version"):
        ProvenanceMetadata("evt-1", "provider:test", now, now, "sha256:abc", "")


def test_marker_provider_requires_implementation() -> None:
    with pytest.raises(NotImplementedError):
        ProvenanceProvider().provenance()


def test_contract_identity_and_immutability() -> None:
    item = _metadata()
    assert PROVENANCE_CONTRACT_ID == "provenance_metadata"
    assert item.contract_version == PROVENANCE_CONTRACT_VERSION
    with pytest.raises(AttributeError):
        item.source = "changed"  # type: ignore[misc]


@pytest.mark.parametrize("field", ["observed_at", "received_at"])
def test_timestamps_must_be_utc(field: str) -> None:
    values: dict[str, Any] = {
        "source_event_id": "evt-1",
        "source": "provider:test",
        "observed_at": datetime(2026, 9, 24, 8, tzinfo=timezone.utc),
        "received_at": datetime(2026, 9, 24, 8, tzinfo=timezone.utc),
        "content_digest": "sha256:abc",
    }
    values[field] = datetime(2026, 9, 24, 8)
    with pytest.raises(ValueError, match="UTC"):
        ProvenanceMetadata(**values)


@pytest.mark.parametrize(
    ("field", "value"), [("source_event_id", ""), ("source", " "), ("content_digest", "")]
)
def test_required_identity_fields_must_not_be_empty(field: str, value: str) -> None:
    values: dict[str, Any] = {
        "source_event_id": "evt-1",
        "source": "provider:test",
        "observed_at": datetime(2026, 9, 24, 8, tzinfo=timezone.utc),
        "received_at": datetime(2026, 9, 24, 8, tzinfo=timezone.utc),
        "content_digest": "sha256:abc",
    }
    values[field] = value
    with pytest.raises(ValueError):
        ProvenanceMetadata(**values)
