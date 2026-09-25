"""FILE: tests/architecture/test_provenance_single_source.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify that provenance metadata has one canonical contract binding.
LAYER: tests
OWNS: Provenance contract registry-binding checks.
DOES_NOT_OWN: production provenance behavior.
DEPENDENCIES: stdlib:pathlib; shared.models.evidence
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from pathlib import Path
from shared.models.evidence import PROVENANCE_CONTRACT_ID, PROVENANCE_CONTRACT_VERSION

ROOT = Path(__file__).resolve().parents[2]


def test_provenance_contract_has_one_registry_binding() -> None:
    registry = (ROOT / "docs" / "contracts.md").read_text(encoding="utf-8")
    assert registry.count(f"| {PROVENANCE_CONTRACT_ID} |") == 1
    assert f'version: "{PROVENANCE_CONTRACT_VERSION}"' in registry


def test_concrete_evidence_files_do_not_shadow_contract_id() -> None:
    for path in (ROOT / "evidence").rglob("*.py"):
        if path.name != "__init__.py":
            assert PROVENANCE_CONTRACT_ID not in path.read_text(encoding="utf-8")
