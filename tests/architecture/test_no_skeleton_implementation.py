"""FILE: tests/architecture/test_no_skeleton_implementation.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Fail verification when an active production module is a frozen skeleton or an unclassified skeleton exists.
LAYER: tests
OWNS: Scope-aware production implementation completeness guard.
DOES_NOT_OWN: Business behavior, provider capability, or release approval.
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


def _skeletons(root: Path) -> list[str]:
    excluded = {".git", ".mypy_cache", ".pytest_cache", ".ruff_cache", "__pycache__", "tests"}
    return sorted(
        str(path.relative_to(root))
        for path in root.rglob("*.py")
        if not any(part in excluded for part in path.relative_to(root).parts)
        and SKELETON_MARKER in path.read_text(encoding="utf-8")
    )


def _manifest(root: Path) -> dict[str, object]:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert data.get("schema_version") == "1.0.0"
    assert data.get("phase_plan") == "docs/adr/0013-phase-plan-implementation-completeness.md"
    entries = data.get("entries")
    assert isinstance(entries, list)
    seen: set[str] = set()
    entries_by_path: dict[str, dict[str, object]] = {}
    for entry in entries:
        assert isinstance(entry, dict)
        path = entry.get("path")
        status = entry.get("status")
        reason = entry.get("reason")
        phase = entry.get("phase")
        owner = entry.get("owner")
        assert isinstance(path, str) and path and path not in seen
        assert status in VALID_STATUSES
        assert isinstance(reason, str) and reason
        assert isinstance(phase, str) and phase
        assert isinstance(owner, str) and owner
        seen.add(path)
        entries_by_path[path] = entry

    scope = data.get("current_scope")
    assert isinstance(scope, dict)
    assert isinstance(scope.get("phase"), str) and scope["phase"]
    assert scope.get("enforcement") == CURRENT_SCOPE_ENFORCEMENT
    scope_entries = scope.get("entries")
    assert isinstance(scope_entries, list) and scope_entries
    assert len(scope_entries) == len(set(scope_entries))
    for path in scope_entries:
        assert isinstance(path, str) and path
        scope_path = root / path
        assert scope_path.is_file()
        if path in entries_by_path:
            assert entries_by_path[path]["status"] == "ACTIVE"
            assert entries_by_path[path]["phase"] == scope["phase"]
    return data


def test_no_active_production_module_is_a_frozen_skeleton() -> None:
    root = Path(__file__).resolve().parents[2]
    data = _manifest(root)
    raw_entries = data["entries"]
    assert isinstance(raw_entries, list)
    entries: dict[str, dict[str, object]] = {
        str(entry["path"]): entry
        for entry in raw_entries
        if isinstance(entry, dict) and isinstance(entry.get("path"), str)
    }
    skeletons = _skeletons(root)
    unknown = sorted(set(skeletons) - set(entries))
    if unknown:
        pytest.fail("Unclassified production skeletons: " + ", ".join(unknown))
    scope = data["current_scope"]
    assert isinstance(scope, dict)
    scope_entries = scope["entries"]
    assert isinstance(scope_entries, list)
    current_scope = set(scope_entries)
    active = sorted(
        path
        for path in skeletons
        if path in current_scope and entries[path].get("status") == "ACTIVE"
    )
    if active:
        pytest.fail(
            "Active production implementation remains a frozen skeleton: " + ", ".join(active)
        )
