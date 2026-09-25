"""FILE: tests/architecture/test_composition_single_source.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify the single canonical signal composition contract and registry binding.
LAYER: tests
OWNS: Architecture-level verification for signal_composition_boundary.
DOES_NOT_OWN: composition production behavior, strategy execution, decision finalization
DEPENDENCIES: stdlib:pathlib; composition.composer
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from pathlib import Path

from composition.composer import COMPOSITION_CONTRACT_ID, COMPOSITION_CONTRACT_VERSION

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "docs" / "contracts.md"
COMPOSITION_ROOT = ROOT / "composition"


def test_composition_contract_has_single_registry_binding() -> None:
    contracts = REGISTRY.read_text(encoding="utf-8")
    assert contracts.count(f"| {COMPOSITION_CONTRACT_ID} |") == 1
    assert f'version: "{COMPOSITION_CONTRACT_VERSION}"' in contracts


def test_composition_contract_id_has_single_source() -> None:
    matches = []
    for path in COMPOSITION_ROOT.rglob("*.py"):
        if path.name == "__init__.py" or path == ROOT / "composition/composer.py":
            continue
        if COMPOSITION_CONTRACT_ID in path.read_text(encoding="utf-8"):
            matches.append(path)
    assert matches == []
