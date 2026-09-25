"""FILE: tests/architecture/test_strategy_single_source.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify the single canonical strategy evaluation contract and registry binding.
LAYER: tests
OWNS: Architecture-level verification for strategy_evaluation_boundary.
DOES_NOT_OWN: strategy production behavior, decision finalization, risk
DEPENDENCIES: stdlib:pathlib; shared.interfaces.strategy
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from pathlib import Path

from shared.interfaces.strategy import STRATEGY_CONTRACT_ID, STRATEGY_CONTRACT_VERSION

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "docs" / "contracts.md"
STRATEGY_ROOT = ROOT / "strategy"


def test_strategy_contract_has_single_registry_binding() -> None:
    contracts = REGISTRY.read_text(encoding="utf-8")
    assert contracts.count(f"| {STRATEGY_CONTRACT_ID} |") == 1
    assert f'version: "{STRATEGY_CONTRACT_VERSION}"' in contracts


def test_strategy_contract_id_has_single_source() -> None:
    matches = []
    for path in STRATEGY_ROOT.rglob("*.py"):
        if path.name == "__init__.py":
            continue
        if STRATEGY_CONTRACT_ID in path.read_text(encoding="utf-8"):
            matches.append(path)
    assert matches == []
