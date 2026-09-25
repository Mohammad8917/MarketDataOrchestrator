"""FILE: tests/architecture/test_indicator_single_source.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify that the canonical indicator contract has one authoritative definition and no shadow contract.
LAYER: tests
OWNS: Static single-source verification for the indicator contract registry binding.
DOES_NOT_OWN: production indicator algorithms, contract definitions, provider I/O
DEPENDENCIES: stdlib:pathlib; indicators.core.base
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from pathlib import Path

from indicators.core.base import INDICATOR_CONTRACT_ID, INDICATOR_CONTRACT_VERSION


def test_indicator_contract_has_one_canonical_definition() -> None:
    repository_root = Path(__file__).resolve().parents[2]
    contracts = (repository_root / "docs" / "contracts.md").read_text(encoding="utf-8")
    assert contracts.count(f"| {INDICATOR_CONTRACT_ID} |") == 1
    assert f'version: "{INDICATOR_CONTRACT_VERSION}"' in contracts


def test_indicator_contract_is_defined_only_at_canonical_boundary() -> None:
    repository_root = Path(__file__).resolve().parents[2]
    indicator_files = repository_root.glob("indicators/**/*.py")
    shadow_ids = []
    for path in indicator_files:
        if path.as_posix().endswith("indicators/core/base.py"):
            continue
        text = path.read_text(encoding="utf-8")
        if INDICATOR_CONTRACT_ID in text:
            shadow_ids.append(str(path))
    assert shadow_ids == []
