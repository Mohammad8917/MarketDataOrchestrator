"""FILE: tests/contract/test_contract_registry_reconciliation.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify executable reconciliation between the authoritative contract registry and the canonical frozen-contract inventory.
LAYER: tests
OWNS: G03 registry/inventory reconciliation verification.
DOES_NOT_OWN: Contract implementation behavior, security threat controls, or release approval.
DEPENDENCIES: validation.contract_registry_validator
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

import json
from validation.contract_registry_validator import DEFAULT_ARTIFACT_PATH, reconcile


def test_contract_registry_matches_frozen_inventory() -> None:
    report = reconcile()
    assert report["status"] == "PASS", report["findings"]
    assert len(report["registry_entries"]) == 11
    assert len(report["inventory_entries"]) == 14
    assert report["findings"] == []
    committed_artifact = json.loads(DEFAULT_ARTIFACT_PATH.read_text(encoding="utf-8"))
    assert committed_artifact == report
