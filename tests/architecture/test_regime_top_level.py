"""FILE: tests/architecture/test_regime_top_level.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify the single canonical regime classification boundary and registry binding.
LAYER: tests
OWNS: Architecture-level verification for regime_classification_boundary.
DOES_NOT_OWN: regime production behavior, strategy execution, decision finalization
DEPENDENCIES: stdlib:pathlib; regime.classification.regime_classifier
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from pathlib import Path

from regime.classification.regime_classifier import (
    REGIME_CONTRACT_ID,
    REGIME_CONTRACT_VERSION,
)


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "docs" / "contracts.md"
REGIME_ROOT = ROOT / "regime"


def test_regime_contract_has_single_registry_binding() -> None:
    contracts = REGISTRY.read_text(encoding="utf-8")
    assert contracts.count(f"| {REGIME_CONTRACT_ID} |") == 1
    assert f'version: "{REGIME_CONTRACT_VERSION}"' in contracts


def test_regime_contract_id_has_single_source() -> None:
    matches = []
    for path in REGIME_ROOT.rglob("*.py"):
        if (
            path.name == "__init__.py"
            or path == ROOT / "regime/classification/regime_classifier.py"
        ):
            continue
        text = path.read_text(encoding="utf-8")
        if REGIME_CONTRACT_ID in text:
            matches.append(path)
    assert matches == []
