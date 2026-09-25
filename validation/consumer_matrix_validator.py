"""FILE: validation/consumer_matrix_validator.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Validate canonical frozen-contract coverage in the G03 runtime consumer matrix.
LAYER: validation
OWNS: Consumer-matrix coverage validation and regression enforcement for frozen contract additions.
DOES_NOT_OWN: Runtime consumer implementation, contract definition, registry ownership, or release approval.
DEPENDENCIES: stdlib:argparse; stdlib:ast; stdlib:json; stdlib:pathlib; stdlib:typing
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
from typing import Any


DEFAULT_INVENTORY = Path("tests/contract/test_frozen_contracts.py")
DEFAULT_MATRIX = Path("evidence/G03_CONSUMER_MATRIX.json")


def _import_map(tree: ast.Module) -> dict[str, str]:
    result: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                if alias.name == "*":
                    continue
                result[alias.asname or alias.name] = f"{node.module}.{alias.name}"
    return result


def frozen_contract_types(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports = _import_map(tree)
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if not any(
                isinstance(target, ast.Name) and target.id == "FROZEN_CONTRACT_TYPES"
                for target in targets
            ):
                continue
            value = node.value
            if not isinstance(value, (ast.Tuple, ast.List)):
                raise ValueError("FROZEN_CONTRACT_TYPES must be a tuple/list")
            resolved: list[str] = []
            for item in value.elts:
                if isinstance(item, ast.Name) and item.id in imports:
                    resolved.append(imports[item.id])
                else:
                    raise ValueError("FROZEN_CONTRACT_TYPES contains an unresolved entry")
            return resolved
    raise ValueError("FROZEN_CONTRACT_TYPES declaration not found")


def matrix_contract_types(path: Path) -> list[str]:
    data: Any = json.loads(path.read_text(encoding="utf-8"))
    contracts = data.get("contracts")
    if not isinstance(contracts, list):
        raise ValueError("consumer matrix contracts must be a list")
    result: list[str] = []
    for entry in contracts:
        if not isinstance(entry, dict) or not isinstance(entry.get("contract"), str):
            raise ValueError("every consumer matrix entry must contain a string contract")
        result.append(entry["contract"])
    return result


def validate(
    inventory_path: Path = DEFAULT_INVENTORY, matrix_path: Path = DEFAULT_MATRIX
) -> list[str]:
    expected = frozen_contract_types(inventory_path)
    actual = matrix_contract_types(matrix_path)

    findings: list[str] = []
    duplicates = sorted({item for item in actual if actual.count(item) > 1})
    if duplicates:
        findings.append("duplicate consumer-matrix contracts: " + ", ".join(duplicates))

    missing = sorted(set(expected) - set(actual))
    if missing:
        findings.append("frozen contracts missing from consumer matrix: " + ", ".join(missing))

    stale = sorted(set(actual) - set(expected))
    if stale:
        findings.append("consumer matrix contains non-frozen/stale contracts: " + ", ".join(stale))

    if len(expected) != len(actual) and not missing and not stale:
        findings.append(
            f"consumer matrix cardinality differs from frozen inventory: expected {len(expected)}, actual {len(actual)}"
        )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX)
    args = parser.parse_args()

    findings = validate(args.inventory, args.matrix)
    if findings:
        print("G03 CONSUMER MATRIX VALIDATION: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print("G03 CONSUMER MATRIX VALIDATION: PASS")
    print(f"- frozen inventory entries: {len(frozen_contract_types(args.inventory))}")
    print(f"- consumer matrix entries: {len(matrix_contract_types(args.matrix))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
