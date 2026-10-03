from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

import validation.contract_registry_validator as validator


def test_registry_parsers_cover_headers_and_signature_boundaries() -> None:
    text = (
        "| contract_id | owner | status | reference |\\n"
        "| --- | --- | --- | --- |\\n"
        "| C1 | x | y | z |\\n"
        "| C2 | x | y | z |\\n"
        "### C1\\n"
        'contract_id: "C1"\\n'
        'signature: "a / b / "'
        "\\n### placeholder\\n"
        'contract_id: "<template>"\\n'
        'signature: "ignored"\\n'
    )
    assert validator._registry_ids(text) == ["C1", "C2"]
    assert validator._registry_signatures(text) == {"C1": ["a", "b"]}


def test_inventory_ast_guards_and_reference_resolution() -> None:
    tree = ast.parse("from package import Alpha as A\\nFROZEN_CONTRACT_TYPES = (A,)\\n")
    assert validator._inventory_imports(tree) == {"A": "package.Alpha"}
    assert validator._inventory_references(tree) == ["package.Alpha"]

    with pytest.raises(ValueError, match="inventory was not found"):
        validator._inventory_declaration(ast.parse("X = 1"))
    with pytest.raises(ValueError, match="tuple/list"):
        validator._inventory_references(ast.parse("FROZEN_CONTRACT_TYPES = 1"))
    with pytest.raises(ValueError, match="unresolved reference"):
        validator._inventory_references(ast.parse("FROZEN_CONTRACT_TYPES = (Missing,)"))


def test_inventory_imports_and_reference_reject_unusable_nodes() -> None:
    tree = ast.parse("import package\\nFROZEN_CONTRACT_TYPES = (A, 1)\\n")
    assert validator._inventory_imports(tree) == {}
    with pytest.raises(ValueError, match="unresolved reference"):
        validator._inventory_references(tree)


def test_frozen_and_resolution_boundaries(monkeypatch: pytest.MonkeyPatch) -> None:
    class Frozen:
        __dataclass_params__ = type("Params", (), {"frozen": True})()

    class Mutable:
        __dataclass_params__ = type("Params", (), {"frozen": False})()

    monkeypatch.setattr(
        validator, "import_module", lambda name: type("Module", (), {"Target": Frozen})()
    )
    assert validator._is_frozen("module.Target") is True
    assert validator._classify_target("C1", "module.Target", Frozen, {}, ["module.Target"])[2]

    monkeypatch.setattr(
        validator, "import_module", lambda name: type("Module", (), {"Target": Mutable})()
    )
    assert validator._is_frozen("module.Target") is False
    target, findings, frozen = validator._classify_target("C1", "module.Target", Mutable, {}, [])
    assert target == {"reference": "module.Target", "kind": "type", "frozen": False}
    assert findings and not frozen

    with pytest.raises(ValueError, match="invalid contract reference"):
        validator._is_frozen("NoModule")


def test_resolve_and_classify_failure_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(_: str):
        raise ImportError("boom")

    monkeypatch.setattr(validator, "import_module", fail)
    target, error = validator._resolve_target("x.Target")
    assert target is None and "boom" in error

    target, findings, frozen = validator._inspect_reference("C1", "x.Target", {}, [])
    assert target is None and findings and not frozen

    def callable_target() -> None:
        return None

    target, findings, frozen = validator._classify_target(
        "C1", "module.callable", callable_target, {}, []
    )
    assert target == {"reference": "module.callable", "kind": "callable", "frozen": False}
    assert not findings and not frozen


def test_contract_inspection_and_inventory_findings() -> None:
    def inspect(contract_id, reference, reasons, inventory):
        return ({"reference": reference, "kind": "type", "frozen": True}, [], True)

    refs = ["a.One", "b.Two"]
    targets, findings, frozen = validator._inspect_contract("C1", refs, {}, refs[:1])
    assert len(targets) == 2 and not findings and frozen == {"a.One", "b.Two"}

    registry_targets, findings = validator._registry_targets(
        ["C1", "C2"], {"C1": refs, "C2": []}, {}, refs[:1]
    )
    assert "C2" in registry_targets
    assert any("no binding" in item for item in findings)
    assert validator._inventory_findings(["a.One", "unused"], registry_targets) == [
        "G03 inventory entry is not referenced by the contract registry: unused"
    ]


def test_registry_shape_and_reconcile_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    assert validator._registry_shape_is_consistent(["C1"], {"C1": ["x"]}, {})
    assert not validator._registry_shape_is_consistent(["C1"], {"C2": ["x"]}, {})

    monkeypatch.setattr(
        validator,
        "_load_inputs",
        lambda: (["C1"], {"C2": ["x"]}, [], {}),
    )
    report = validator.reconcile()
    assert report["status"] == "FAIL"
    assert report["findings"]


def test_write_artifact_and_main_status(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    report = {
        "status": "PASS",
        "findings": [],
        "registry_entries": [],
        "inventory_entries": [],
    }
    path = tmp_path / "artifact.json"
    validator.write_artifact(report, path)
    assert json.loads(path.read_text(encoding="utf-8")) == report

    monkeypatch.setattr(validator, "reconcile", lambda: report)
    monkeypatch.setattr(validator, "DEFAULT_ARTIFACT_PATH", path)
    assert validator.main() == 0
    assert "PASS" in capsys.readouterr().out

    failed = {**report, "status": "FAIL", "findings": ["bad"]}
    monkeypatch.setattr(validator, "reconcile", lambda: failed)
    assert validator.main() == 1
