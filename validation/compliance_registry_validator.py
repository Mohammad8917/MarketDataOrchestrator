"""
FILE: validation/compliance_registry_validator.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Validate the canonical compliance registry structure and control-to-gate bindings
LAYER: validation
OWNS: Compliance registry structural validation
DOES_NOT_OWN: Runtime behavior, provider capability verification, release artifact generation
DEPENDENCIES: stdlib, validation.markdown_registry
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

from validation.markdown_registry import extract_contract_ids_from_md

ROOT = Path(__file__).resolve().parents[1]
COMPLIANCE = ROOT / "docs" / "README.md"
CONTRACTS = ROOT / "docs" / "contracts.md"
CAPABILITIES = ROOT / "docs" / "capability-matrix.md"

GATES = {
    "G01_FORMAT_LINT",
    "G02_TYPECHECK",
    "G03_UNIT_CONTRACT",
    "G04_ARCHITECTURE_DEPENDENCY",
    "G05_COVERAGE",
    "G06_SECURITY_SUPPLY_CHAIN",
    "G07_INTEGRATION_RESILIENCE",
    "G08_RELEASE_VERIFICATION",
}


def fail(message: str) -> None:
    print(f"COMPLIANCE REGISTRY: FAIL: {message}", file=sys.stderr)


def main() -> int:
    for path in (COMPLIANCE, CONTRACTS, CAPABILITIES):
        if not path.is_file():
            fail(f"missing canonical registry: {path.relative_to(ROOT)}")
            return 1

    compliance = COMPLIANCE.read_text(encoding="utf-8")
    contracts = CONTRACTS.read_text(encoding="utf-8")
    capabilities = CAPABILITIES.read_text(encoding="utf-8")

    control_ids = re.findall(r"^\| (C\d+_[A-Z0-9_]+) \|", compliance, re.MULTILINE)
    appendix_ids = re.findall(r"^\| ([A-J]) \| (APP-[A-J]-\d+) \| (G\d+_[A-Z_]+) \|", compliance, re.MULTILINE)
    gate_ids = set(re.findall(r"^\| (G\d+_[A-Z_]+) \|", compliance, re.MULTILINE))
    contract_registry = contracts.split("## Typed contract bindings", 1)[0]
    contract_ids = re.findall(r"^\| ([a-z0-9_]+) \|", contract_registry, re.MULTILINE)[1:]
    rate_ids = re.findall(r"^\| (rate_[a-z0-9]+) \|", capabilities, re.MULTILINE)

    if len(control_ids) != len(set(control_ids)) or not control_ids:
        fail("Compliance Matrix control IDs are missing or duplicated")
        return 1
    if len(appendix_ids) != len(set(item[1] for item in appendix_ids)):
        fail("Appendix control IDs are duplicated")
        return 1
    if gate_ids != GATES:
        fail("mandatory G01-G08 gate set is incomplete")
        return 1
    if any(gate not in GATES for _, _, gate in appendix_ids):
        fail("appendix control references an unknown CI gate")
        return 1
    expected_contracts = {
        "ingestion_provider_boundary",
        "market_data_event",
        "provenance_metadata",
        "temporal_event_boundary",
        "validation_result",
        "equity_curve",
    }
    if set(contract_ids) != expected_contracts:
        fail("contract registry IDs do not match the six-contract baseline established by ADR-017")
        return 1
    if len(rate_ids) != 15:
        fail("provider/rate registry baseline is incomplete")
        return 1

    market_binding = re.search(
        r'contract_id: "market_data_event".*?signature: "([^"]+)".*?tests: \["([^"]+)"\]',
        contracts,
        re.DOTALL,
    )
    if market_binding is None:
        fail("market_data_event typed binding record is missing")
        return 1
    signature, test_path = market_binding.groups()
    expected_signature = "domain.market_data_event.MarketDataEvent"
    if signature != expected_signature:
        fail(f"market_data_event signature mismatch: {signature!r}")
        return 1
    if not (ROOT / "domain" / "market_data_event.py").is_file():
        fail("market_data_event implementation is missing")
        return 1
    if not (ROOT / test_path).is_file():
        fail(f"market_data_event contract test is missing: {test_path}")
        return 1

    equity_binding = re.search(
        r'contract_id: "equity_curve".*?signature: "([^"]+)"',
        contracts,
        re.DOTALL,
    )
    if equity_binding is None:
        fail("equity_curve typed binding record is missing")
        return 1
    equity_signature = equity_binding.group(1)
    if equity_signature != "shared.contracts.equity_curve.EquityCurve":
        fail(f"equity_curve signature mismatch: {equity_signature!r}")
        return 1
    if not (ROOT / "shared" / "contracts" / "equity_curve.py").is_file():
        fail("equity_curve interface is missing")
        return 1

    print(
        "COMPLIANCE REGISTRY: PASS "
        f"(controls={len(control_ids)}, appendix_controls={len(appendix_ids)}, "
        f"contracts={len(contract_ids)}, rate_limits={len(rate_ids)}, gates=8)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
