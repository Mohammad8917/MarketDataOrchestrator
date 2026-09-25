"""FILE: tests/validation/test_architecture_dependency_validator.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Exercise architecture dependency validator parsing, graph, ownership, and failure paths.
LAYER: tests
OWNS: Validator unit and failure-path coverage.
DOES_NOT_OWN: Production architecture policy or runtime orchestration.
DEPENDENCIES: pytest; validation.architecture_dependency_validator
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

import ast
import runpy
from pathlib import Path

import pytest

from validation import architecture_dependency_validator as validator


def _header(path: str, layer: str, dependencies: str = "None declared") -> str:
    return f'''"""FILE: {path}
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: Test
RESPONSIBILITY: test
LAYER: {layer}
OWNS: test
DOES_NOT_OWN: test
DEPENDENCIES: {dependencies}
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Test
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""
'''


def test_header_and_dependency_parsers_cover_normal_and_edge_cases() -> None:
    header, ordered = validator.parse_header("A: one\nB: two\ninvalid")
    assert header == {"A": "one", "B": "two"}
    assert ordered == ["A", "B"]

    assert validator.declared_project_dependencies("None declared") == set()
    assert validator.declared_project_dependencies("validation.foo, reason; shared.models") == {
        "validation",
        "shared",
    }

    tree = ast.parse(
        "import validation.foo\nfrom shared.models import evidence\nfrom .local import x"
    )
    assert validator.imported_project_layers(tree) == {"validation", "shared"}
    assert validator.imported_modules(tree, "tests.validation.sample") == {
        "validation.foo",
        "shared.models",
    }


def test_path_and_module_resolution_helpers(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(validator, "ROOT", tmp_path)
    monkeypatch.setattr(validator, "SOURCE_ROOTS", {"shared", "validation"})

    shared = tmp_path / "shared"
    package = shared / "models"
    package.mkdir(parents=True)
    (shared / "__init__.py").write_text("", encoding="utf-8")
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "item.py").write_text("", encoding="utf-8")

    assert validator.layer_of(package / "item.py") == "shared"
    assert validator.layer_of(tmp_path / "other.py") is None
    assert validator.resolve_module("shared.models.item") == package / "item.py"
    assert validator.resolve_module("shared.models") == package / "__init__.py"
    assert validator.resolve_module("external.item") is None
    assert validator.module_name_for(package / "__init__.py") == "shared.models"
    assert validator.module_name_for(package / "item.py") == "shared.models.item"

    tree = ast.parse("from .models import item\nfrom ..shared import x")
    assert validator.imported_modules(tree, "shared.submodule") == {"shared.models", "shared"}


def test_main_passes_for_a_clean_minimal_tree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(validator, "ROOT", tmp_path)
    monkeypatch.setattr(validator, "SOURCE_ROOTS", {"shared"})
    monkeypatch.setattr(validator, "ALLOWED", {"shared": {"shared"}})
    monkeypatch.setattr(validator, "FORBIDDEN", {"shared": set()})

    path = tmp_path / "shared" / "clean.py"
    path.parent.mkdir()
    path.write_text(_header("shared/clean.py", "shared"), encoding="utf-8")

    assert validator.main() == 0


@pytest.mark.parametrize(
    "body",
    [
        '"""broken\n',
        _header("wrong.py", "shared").replace("FILE: wrong.py", "FILE: other.py"),
        _header("shared/bad.py", "validation"),
        _header("shared/bad.py", "shared", "validation"),
    ],
)
def test_main_rejects_invalid_source_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, body: str
) -> None:
    monkeypatch.setattr(validator, "ROOT", tmp_path)
    monkeypatch.setattr(validator, "SOURCE_ROOTS", {"shared", "validation"})
    monkeypatch.setattr(validator, "ALLOWED", {"shared": {"shared"}, "validation": {"shared"}})
    monkeypatch.setattr(validator, "FORBIDDEN", {"shared": {"validation"}, "validation": set()})

    path = tmp_path / "shared" / "bad.py"
    path.parent.mkdir()
    path.write_text(body, encoding="utf-8")

    assert validator.main() == 1


def test_main_rejects_missing_fields_dependency_direction_and_cycles(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(validator, "ROOT", tmp_path)
    monkeypatch.setattr(validator, "SOURCE_ROOTS", {"shared", "validation"})
    monkeypatch.setattr(validator, "ALLOWED", {"shared": {"shared"}, "validation": {"shared"}})
    monkeypatch.setattr(validator, "FORBIDDEN", {"shared": {"validation"}, "validation": set()})

    shared = tmp_path / "shared"
    validation = tmp_path / "validation"
    shared.mkdir()
    validation.mkdir()

    missing = shared / "missing.py"
    missing.write_text(
        '"""FILE: shared/missing.py\nKIT: x\n"""\nimport validation.tool\n',
        encoding="utf-8",
    )
    (validation / "tool.py").write_text(
        _header("validation/tool.py", "validation", "shared"), encoding="utf-8"
    )
    (shared / "a.py").write_text(
        _header("shared/a.py", "shared", "shared") + "import shared.b\n",
        encoding="utf-8",
    )
    (shared / "b.py").write_text(
        _header("shared/b.py", "shared", "shared") + "import shared.a\n",
        encoding="utf-8",
    )

    assert validator.main() == 1


def test_main_reports_syntax_errors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(validator, "ROOT", tmp_path)
    monkeypatch.setattr(validator, "SOURCE_ROOTS", {"shared"})
    monkeypatch.setattr(validator, "ALLOWED", {"shared": {"shared"}})
    monkeypatch.setattr(validator, "FORBIDDEN", {"shared": set()})

    path = tmp_path / "shared" / "syntax.py"
    path.parent.mkdir()
    path.write_text("def broken(:\n", encoding="utf-8")

    assert validator.main() == 1


def test_remaining_validator_branches_and_module_guard(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(validator, "ROOT", tmp_path)
    monkeypatch.setattr(validator, "SOURCE_ROOTS", {"shared"})
    monkeypatch.setattr(validator, "ALLOWED", {"shared": {"shared"}})
    monkeypatch.setattr(validator, "FORBIDDEN", {"shared": set()})

    assert validator.imported_project_layers(ast.parse("import external.mod")) == set()
    assert validator.imported_project_layers(ast.parse("from external import mod")) == set()
    assert validator.declared_project_dependencies("") == set()

    assert validator.resolve_module("shared.missing") is None
    tree = ast.parse("from . import x")
    assert validator.imported_modules(tree, "shared") == set()

    outside = tmp_path / "outside.py"
    outside.write_text("x = 1\n", encoding="utf-8")
    shared = tmp_path / "shared"
    shared.mkdir()
    clean = shared / "clean.py"
    clean.write_text(
        _header("shared/clean.py", "shared", "shared")
        + "import shared.clean\nimport shared.missing\n",
        encoding="utf-8",
    )
    assert validator.main() == 0

    cycle_a = shared / "a.py"
    cycle_b = shared / "b.py"
    cycle_a.write_text(
        _header("shared/a.py", "shared", "shared") + "import shared.b\n",
        encoding="utf-8",
    )
    cycle_b.write_text(
        _header("shared/b.py", "shared", "shared") + "import shared.a\nimport shared.clean\n",
        encoding="utf-8",
    )
    assert validator.main() == 1

    with pytest.raises(SystemExit):
        runpy.run_path(str(Path(validator.__file__)), run_name="__main__")
