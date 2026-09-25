"""FILE: validation/compliance_registry_validator.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Validate the canonical compliance registry structure and control-to-gate bindings.
LAYER: validation
OWNS: Compliance registry structural validation.
DOES_NOT_OWN: Runtime behavior, provider capability verification, release artifact generation.
DEPENDENCIES: stdlib:pathlib; stdlib:re; stdlib:sys
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

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
    appendix_ids = re.findall(
        r"^\| ([A-J]) \| (APP-[A-J]-\d+) \| (G\d+_[A-Z_]+) \|",
        compliance,
        re.MULTILINE,
    )
    gate_ids = set(re.findall(r"^\| (G\d+_[A-Z_]+) \|", compliance, re.MULTILINE))
    contract_ids = re.findall(r"^\| (?!contract_id\b)([a-z0-9_]+) \|", contracts, re.MULTILINE)
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
    if len(contract_ids) < 1 or len(rate_ids) != 15:
        fail("contract or provider/rate registry baseline is incomplete")
        return 1

    print(
        "COMPLIANCE REGISTRY: PASS "
        f"(controls={len(control_ids)}, appendix_controls={len(appendix_ids)}, "
        f"contracts={len(contract_ids)}, rate_limits={len(rate_ids)}, gates=8)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
