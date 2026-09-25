"""FILE: tests/architecture/test_no_skeleton_tests.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Fail verification when an active test module is a frozen skeleton or an unclassified skeleton exists.
LAYER: tests
OWNS: Scope-aware test-suite completeness guard.
DOES_NOT_OWN: Production implementation behavior or production architecture policy.
DEPENDENCIES: stdlib:json; stdlib:pathlib; pytest
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

import json
from pathlib import Path

import pytest


SKELETON_MARKER = "Frozen skeleton; executable implementation is intentionally deferred"
MANIFEST = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "compliance"
    / "IMPLEMENTATION_PHASE_MANIFEST.json"
)
VALID_STATUSES = {"ACTIVE", "EXCLUDED", "DEFERRED"}
CURRENT_SCOPE_ENFORCEMENT = "CURRENT_SCOPE_ONLY"


def _manifest() -> dict[str, dict[str, str]]:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert data.get("schema_version") == "1.0.0"
    entries = data.get("entries")
    assert isinstance(entries, list)
    result: dict[str, dict[str, str]] = {}
    for entry in entries:
        assert isinstance(entry, dict)
        path = entry.get("path")
        status = entry.get("status")
        reason = entry.get("reason")
        phase = entry.get("phase")
        owner = entry.get("owner")
        assert isinstance(path, str) and path
        assert isinstance(status, str) and status in VALID_STATUSES
        assert isinstance(reason, str) and reason
        assert isinstance(phase, str) and phase
        assert isinstance(owner, str) and owner
        assert path not in result
        result[path] = {
            "status": status,
            "reason": reason,
            "phase": phase,
            "owner": owner,
        }
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert data.get("schema_version") == "1.0.0"
    scope = data.get("current_scope")
    assert isinstance(scope, dict)
    assert isinstance(scope.get("phase"), str) and scope["phase"]
    assert scope.get("enforcement") == CURRENT_SCOPE_ENFORCEMENT
    scope_entries = scope.get("entries")
    assert isinstance(scope_entries, list) and scope_entries
    assert len(scope_entries) == len(set(scope_entries))
    root = MANIFEST.resolve().parents[2]
    for path in scope_entries:
        assert isinstance(path, str)
        assert (root / path).is_file()
        if path in result:
            assert result[path]["status"] == "ACTIVE"
            assert result[path]["phase"] == scope["phase"]
    return result


def test_no_active_test_module_is_a_frozen_skeleton() -> None:
    root = Path(__file__).resolve().parents[2]
    manifest = _manifest()
    skeletons = sorted(
        str(path.relative_to(root))
        for path in root.rglob("test_*.py")
        if path != Path(__file__) and SKELETON_MARKER in path.read_text(encoding="utf-8")
    )
    unknown = sorted(set(skeletons) - set(manifest))
    if unknown:
        pytest.fail("Unclassified test skeletons: " + ", ".join(unknown))
    scope = json.loads(MANIFEST.read_text(encoding="utf-8"))["current_scope"]
    assert isinstance(scope, dict)
    scope_entries = scope["entries"]
    assert isinstance(scope_entries, list)
    current_scope = set(scope_entries)
    active = sorted(
        path for path in skeletons if path in current_scope and manifest[path]["status"] == "ACTIVE"
    )
    if active:
        pytest.fail(
            "Active executable verification remains a frozen skeleton: " + ", ".join(active)
        )
