"""FILE: validation/architecture_dependency_validator.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.1.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Validate Python source ownership headers and the frozen file/layer dependency direction.
LAYER: validation
OWNS: Cross-layer architecture dependency validation, header ownership validation, declared direct-dependency validation, and cycle detection.
DOES_NOT_OWN: Runtime orchestration, provider capability verification, release artifact generation, or business logic.
DEPENDENCIES: ast, pathlib, sys
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

import ast
import re
from collections.abc import Hashable
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOTS = {
    "analysis",
    "backtest",
    "composition",
    "config",
    "core",
    "decision",
    "domain",
    "domain_adapters",
    "evidence",
    "feedback",
    "indicators",
    "ingestion",
    "output",
    "persistence",
    "regime",
    "risk",
    "shared",
    "strategy",
    "validation",
    "app",
}
TEST_ROOT = "tests"

ALLOWED = {
    "app": {"core", "config", "shared"},
    "core": {"config", "shared", "ingestion", "persistence", "validation", "output"},
    "config": {"shared"},
    "shared": {"shared"},
    "domain": {"shared"},
    "ingestion": {"shared", "config", "domain", "ingestion"},
    "domain_adapters": {"domain", "ingestion", "shared"},
    "indicators": {"shared", "domain", "indicators"},
    "analysis": {"indicators", "domain", "ingestion", "shared", "regime", "volatility"},
    "regime": {"indicators", "domain", "shared"},
    "composition": {"indicators", "analysis", "regime", "shared"},
    "strategy": {"analysis", "regime", "composition", "shared"},
    "evidence": {"analysis", "composition", "regime", "strategy", "shared"},
    "decision": {"evidence", "strategy", "regime", "shared"},
    "risk": {"decision", "domain", "shared", "config"},
    "persistence": {"shared", "domain"},
    "feedback": {"backtest", "persistence", "shared"},
    "output": {"shared"},
    "validation": {"ingestion", "evidence", "decision", "risk", "shared"},
    "tests": set(SOURCE_ROOTS),
    "scripts": {"shared", "validation"},
    "backtest": {
        "ingestion",
        "indicators",
        "analysis",
        "regime",
        "composition",
        "strategy",
        "evidence",
        "decision",
        "risk",
        "validation",
        "domain",
        "shared",
    },
}

FORBIDDEN = {
    "core": {"app", "analysis", "indicators", "strategy", "decision", "risk"},
    "shared": SOURCE_ROOTS - {"shared"},
    "domain": {"app", "core", "ingestion", "analysis", "strategy", "decision", "risk"},
    "ingestion": {"analysis", "indicators", "strategy", "decision", "risk", "persistence"},
    "domain_adapters": {"analysis", "strategy", "decision", "risk", "persistence"},
    "indicators": {"analysis", "strategy", "decision", "risk", "ingestion"},
    "analysis": {"strategy", "decision", "risk"},
    "regime": {"strategy", "decision", "risk"},
    "composition": {"decision", "risk", "persistence"},
    "strategy": {"evidence", "decision", "risk", "persistence"},
    "evidence": {"decision", "risk", "persistence"},
    "decision": {"risk", "persistence", "output"},
    "risk": {"strategy", "evidence", "output", "ingestion"},
    "persistence": {"ingestion", "strategy", "decision", "risk", "output"},
    "feedback": {"strategy", "decision", "risk", "ingestion"},
    "output": {"decision", "risk", "ingestion", "persistence"},
    "validation": {"strategy", "persistence", "output"},
    "tests": set(),
    "scripts": set(),
}

HEADER_FIELDS = (
    "FILE",
    "KIT",
    "FILE_VERSION",
    "DATE_GREGORIAN",
    "DATE_PERSIAN",
    "AUTHOR",
    "RESPONSIBILITY",
    "LAYER",
    "OWNS",
    "DOES_NOT_OWN",
    "DEPENDENCIES",
    "PYTHON",
    "LICENSE",
    "NOTICE",
    "COMPLIANCE",
)


def layer_of(path: Path) -> str | None:
    parts = path.relative_to(ROOT).parts
    return parts[0] if parts and parts[0] in SOURCE_ROOTS else None


def parse_header(doc: str) -> tuple[dict[str, str], list[str]]:
    lines = doc.splitlines()
    out: dict[str, str] = {}
    ordered: list[str] = []
    for line in lines[: len(HEADER_FIELDS)]:
        if ":" not in line:
            break
        key, value = line.split(":", 1)
        key = key.strip()
        ordered.append(key)
        out[key] = value.strip()
    return out, ordered


def imported_project_layers(tree: ast.AST) -> set[str]:
    layers: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = node.names
        elif isinstance(node, ast.ImportFrom) and not node.level:
            module = node.module or ""
            root = module.split(".", 1)[0]
            if root in SOURCE_ROOTS:
                layers.add(root)
            continue
        else:
            continue
        for alias in names:
            root = alias.name.split(".", 1)[0]
            if root in SOURCE_ROOTS:
                layers.add(root)
    return layers


def cross_layer_imports(source_layer: str, imported_layers: set[str]) -> set[str]:
    """Return only dependencies that cross the source layer boundary."""
    return imported_layers - {source_layer}


def dependency_allowed(source_layer: str, target_layer: str) -> bool:
    """Return whether a project-layer dependency is permitted by the frozen rules."""
    return target_layer in ALLOWED.get(source_layer, set()) and target_layer not in FORBIDDEN.get(
        source_layer, set()
    )


def declared_project_dependencies(value: str) -> set[str]:
    if not value or value.lower().startswith("none declared"):
        return set()
    declared: set[str] = set()
    for item in value.replace(";", ",").split(","):
        token = item.strip()
        root = token.split(".", 1)[0]
        if root in SOURCE_ROOTS:
            declared.add(root)
    return declared


def resolve_module(module: str) -> Path | None:
    parts = module.split(".")
    if not parts or parts[0] not in SOURCE_ROOTS:
        return None
    base = ROOT.joinpath(*parts)
    candidate = base.with_suffix(".py")
    if candidate.is_file():
        return candidate
    init = base / "__init__.py"
    if init.is_file():
        return init
    return None


def module_name_for(path: Path) -> str:
    rel = path.relative_to(ROOT).with_suffix("")
    parts = list(rel.parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _absolute_import_module(node: ast.ImportFrom) -> str:
    return node.module or ""


def _relative_import_module(node: ast.ImportFrom, current_parts: list[str]) -> str:
    prefix = current_parts[: -node.level]
    target = prefix + (node.module or "").split(".")
    return ".".join(target)


def _import_from_module(node: ast.ImportFrom, current_parts: list[str]) -> str:
    if node.level:
        return _relative_import_module(node, current_parts)
    return _absolute_import_module(node)


def imported_modules(tree: ast.AST, current_module: str) -> set[str]:
    modules: set[str] = set()
    current_parts = current_module.split(".")
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(_project_import_names(node))
        elif isinstance(node, ast.ImportFrom):
            module = _import_from_module(node, current_parts)
            if _is_project_module(module):
                modules.add(module)
    return modules


def _project_import_names(node: ast.Import) -> set[str]:
    return {alias.name for alias in node.names if _is_project_module(alias.name)}


def _is_project_module(module: str) -> bool:
    return bool(module) and module.split(".", 1)[0] in SOURCE_ROOTS


def find_cycles[T: Hashable](graph: dict[T, set[T]]) -> list[str]:
    """Return deterministic dependency-cycle descriptions for a directed graph."""
    cycles: list[str] = []
    visiting: set[T] = set()
    visited: set[T] = set()

    def visit(node: T, stack: list[T]) -> None:
        if node in visiting:
            cycle = stack[stack.index(node) :] + [node] if node in stack else stack + [node]
            cycles.append("dependency cycle: " + " -> ".join(map(str, cycle)))
            return
        if node in visited:
            return
        visiting.add(node)
        for target in sorted(graph.get(node, set()), key=str):
            visit(target, stack + [node])
        visiting.remove(node)
        visited.add(node)

    for node in sorted(graph, key=str):
        visit(node, [])
    return cycles


def _header_from_source(source: str, tree: ast.Module) -> tuple[dict[str, str], list[str]]:
    raw_header = re.match(r"^\"\"\"(.*?)\"\"\"", source, re.DOTALL)
    raw_doc = raw_header.group(1).lstrip("\n") if raw_header else ""
    doc = ast.get_docstring(tree, clean=False)
    return parse_header(raw_doc or doc or "")


def _validate_header(
    path: Path, layer: str, header: dict[str, str], ordered: list[str]
) -> list[str]:
    failures: list[str] = []
    if ordered != list(HEADER_FIELDS):
        failures.append(f"{path}: non-canonical header field order/schema")
    if header.get("FILE") != path.relative_to(ROOT).as_posix():
        failures.append(f"{path}: FILE header does not match repository path")
    failures.extend(f"{path}: missing {key}" for key in HEADER_FIELDS if not header.get(key))
    if header.get("LAYER") != layer:
        failures.append(f"{path}: declared LAYER={header.get('LAYER')!r}, expected {layer!r}")
    return failures


def _validate_dependencies(
    path: Path, layer: str, imported: set[str], header: dict[str, str]
) -> list[str]:
    declared = declared_project_dependencies(header.get("DEPENDENCIES", ""))
    if imported != declared:
        return [
            f"{path}: DEPENDENCIES mismatch; declared={sorted(declared)}, actual={sorted(imported)}"
        ]
    return [
        f"{path}: forbidden dependency {layer} -> {target}"
        for target in _forbidden_dependencies(layer, imported)
    ]


def _forbidden_dependencies(layer: str, imported: set[str]) -> set[str]:
    cross_layer = cross_layer_imports(layer, imported)
    return {target for target in cross_layer if not dependency_allowed(layer, target)}


def _scan_file(path: Path) -> tuple[list[str], str, set[str], set[Path]]:
    layer = layer_of(path)
    if layer is None:
        return [], "", set(), set()
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    header, ordered = _header_from_source(source, tree)
    failures = _validate_header(path, layer, header, ordered)
    imported = imported_project_layers(tree)
    failures.extend(_validate_dependencies(path, layer, imported, header))
    targets = _resolve_import_targets(path, tree)
    return failures, layer, imported, targets


def _resolve_import_targets(path: Path, tree: ast.AST) -> set[Path]:
    graph_targets: set[Path] = set()
    source_module = module_name_for(path)
    for module in imported_modules(tree, source_module):
        target = resolve_module(module)
        if target is not None and target != path:
            graph_targets.add(target)
    return graph_targets


def _scan_repository() -> tuple[list[str], dict[str, set[str]], dict[Path, set[Path]]]:
    failures: list[str] = []
    layer_graph: dict[str, set[str]] = {}
    file_graph: dict[Path, set[Path]] = {}
    for path in sorted(ROOT.rglob("*.py")):
        try:
            file_failures, layer, imported, targets = _scan_file(path)
        except SyntaxError as exc:
            failures.append(f"{path}: syntax error: {exc}")
            continue
        if not layer:
            continue
        failures.extend(file_failures)
        layer_graph.setdefault(layer, set()).update(cross_layer_imports(layer, imported))
        file_graph.setdefault(path, set()).update(targets)
    return failures, layer_graph, file_graph


def main() -> int:
    failures, layer_graph, file_graph = _scan_repository()
    failures.extend(find_cycles(file_graph))
    failures.extend(find_cycles(layer_graph))
    if failures:
        print("ARCHITECTURE DEPENDENCY: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("ARCHITECTURE DEPENDENCY: PASS")
    print(f"- files scanned: {len(file_graph)}")
    print(f"- layers scanned: {len(layer_graph)}")
    print(f"- file dependency edges: {sum(len(v) for v in file_graph.values())}")
    print(f"- layer dependency edges: {sum(len(v) for v in layer_graph.values())}")
    print("- cycles: none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
