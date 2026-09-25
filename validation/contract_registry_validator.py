"""FILE: validation/contract_registry_validator.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Reconcile the authoritative contract registry with the executable frozen-contract inventory and ADR immutability rationale.
LAYER: validation
OWNS: Registry-to-inventory reconciliation, frozen/non-frozen classification, and machine-readable G03 evidence generation.
DOES_NOT_OWN: Contract implementation behavior, security threat controls, release provenance, or registry business semantics.
DEPENDENCIES: stdlib:ast; stdlib:dataclasses; stdlib:importlib; stdlib:json; stdlib:pathlib; stdlib:typing
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from importlib import import_module
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "docs" / "contracts.md"
INVENTORY_PATH = ROOT / "tests" / "contract" / "test_frozen_contracts.py"
ADR_PATH = ROOT / "docs" / "adr" / "0009-frozen-contract-reverse-guards.md"
DEFAULT_ARTIFACT_PATH = ROOT / "evidence" / "G03_CONTRACT_REGISTRY_RECONCILIATION.json"


@dataclass(frozen=True, slots=True)
class RegistryTarget:
    contract_id: str
    reference: str


def _registry_ids(text: str) -> list[str]:
    ids: list[str] = []
    for line in text.splitlines():
        if not line.startswith("| ") or "contract_id" in line:
            continue
        columns = [part.strip() for part in line.strip("|").split("|")]
        if len(columns) >= 4 and columns[0] and columns[0] != "---":
            ids.append(columns[0])
    return ids


def _registry_signatures(text: str) -> dict[str, list[str]]:
    signatures: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        if line.startswith("### "):
            current = None
        if line.startswith('contract_id: "') and line.endswith('"'):
            candidate = line[len('contract_id: "') : -1]
            current = None if candidate.startswith("<") else candidate
        elif current is not None and line.startswith('signature: "') and line.endswith('"'):
            raw = line[len('signature: "') : -1]
            signatures[current] = [item.strip() for item in raw.split("/") if item.strip()]
            current = None
    return signatures


def _inventory_references(tree: ast.Module) -> list[str]:
    imported: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                imported[alias.asname or alias.name] = f"{node.module}.{alias.name}"

    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Name) and target.id == "FROZEN_CONTRACT_TYPES"
            for target in node.targets
        ):
            continue
        if not isinstance(node.value, (ast.Tuple, ast.List)):
            raise ValueError("FROZEN_CONTRACT_TYPES must be a tuple/list")
        references: list[str] = []
        for item in node.value.elts:
            if isinstance(item, ast.Name) and item.id in imported:
                references.append(imported[item.id])
            else:
                raise ValueError("FROZEN_CONTRACT_TYPES contains an unresolved reference")
        return references
    raise ValueError("FROZEN_CONTRACT_TYPES inventory was not found")


def _is_frozen(reference: str) -> bool:
    module_name, _, attr_name = reference.rpartition(".")
    if not module_name:
        raise ValueError(f"invalid contract reference: {reference}")
    target = getattr(import_module(module_name), attr_name)
    params = getattr(target, "__dataclass_params__", None)
    return bool(params is not None and getattr(params, "frozen", False) is True)


def _adr_reasons(text: str) -> dict[str, str]:
    reasons: dict[str, str] = {}
    in_section = False
    for line in text.splitlines():
        if line.strip() == "## Registry reconciliation":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if not in_section or not line.startswith("| ") or "contract_id" in line or "---" in line:
            continue
        columns = [part.strip() for part in line.strip("|").split("|")]
        if len(columns) >= 2 and columns[0]:
            reasons[columns[0]] = columns[1]
    return reasons


def reconcile() -> dict[str, Any]:
    registry_text = REGISTRY_PATH.read_text(encoding="utf-8")
    inventory_tree = ast.parse(INVENTORY_PATH.read_text(encoding="utf-8"))
    adr_text = ADR_PATH.read_text(encoding="utf-8")

    registry_ids = _registry_ids(registry_text)
    signatures = _registry_signatures(registry_text)
    inventory = _inventory_references(inventory_tree)
    reasons = _adr_reasons(adr_text)

    findings: list[str] = []
    targets_by_registry: dict[str, list[dict[str, Any]]] = {}
    referenced_inventory: set[str] = set()

    for contract_id in registry_ids:
        refs = signatures.get(contract_id, [])
        if not refs:
            if contract_id not in reasons:
                findings.append(
                    f"registry entry has no binding and no documented non-frozen reason: {contract_id}"
                )
            targets_by_registry[contract_id] = []
            continue

        targets: list[dict[str, Any]] = []
        for reference in refs:
            module_name, _, attr_name = reference.rpartition(".")
            try:
                target = getattr(import_module(module_name), attr_name)
            except (ImportError, AttributeError, ValueError) as exc:
                findings.append(
                    f"registry binding cannot be resolved: {contract_id} -> {reference}: {exc}"
                )
                continue

            if isinstance(target, type):
                try:
                    frozen = _is_frozen(reference)
                except (ImportError, AttributeError, ValueError) as exc:
                    findings.append(
                        f"registry target cannot be classified: {contract_id} -> {reference}: {exc}"
                    )
                    continue
                if frozen:
                    referenced_inventory.add(reference)
                    if reference not in inventory:
                        findings.append(
                            f"frozen registry target is missing from G03 inventory: {contract_id} -> {reference}"
                        )
                elif contract_id not in reasons:
                    findings.append(
                        f"non-frozen registry target has no ADR reason: {contract_id} -> {reference}"
                    )
                targets.append({"reference": reference, "kind": "type", "frozen": frozen})
            else:
                if contract_id not in reasons:
                    findings.append(
                        f"non-type registry target has no ADR reason: {contract_id} -> {reference}"
                    )
                targets.append({"reference": reference, "kind": "callable", "frozen": False})

        targets_by_registry[contract_id] = targets

    registry_refs = {
        target["reference"] for targets in targets_by_registry.values() for target in targets
    }
    for reference in inventory:
        if reference not in registry_refs:
            findings.append(
                f"G03 inventory entry is not referenced by the contract registry: {reference}"
            )

    if set(registry_ids) != set(signatures) | {
        contract_id
        for contract_id in registry_ids
        if contract_id in reasons and not signatures.get(contract_id)
    }:
        findings.append("registry parsing produced an inconsistent contract-id/signature set")

    return {
        "schema_version": "1.0.0",
        "registry": str(REGISTRY_PATH.relative_to(ROOT)),
        "inventory": str(INVENTORY_PATH.relative_to(ROOT)),
        "adr": str(ADR_PATH.relative_to(ROOT)),
        "registry_entries": registry_ids,
        "inventory_entries": inventory,
        "registry_targets": targets_by_registry,
        "adr_non_frozen_reasons": reasons,
        "findings": sorted(set(findings)),
        "status": "PASS" if not findings else "FAIL",
    }


def write_artifact(report: dict[str, Any], path: Path = DEFAULT_ARTIFACT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    report = reconcile()
    write_artifact(report)
    print(f"G03 CONTRACT REGISTRY RECONCILIATION: {report['status']}")
    for finding in report["findings"]:
        print(f"- {finding}")
    print(f"- registry entries: {len(report['registry_entries'])}")
    print(f"- frozen inventory entries: {len(report['inventory_entries'])}")
    print(f"- artifact: {DEFAULT_ARTIFACT_PATH.relative_to(ROOT)}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
