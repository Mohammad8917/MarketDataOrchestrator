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
    "analysis": {"indicators", "domain", "ingestion", "shared"},
    "regime": {"analysis", "indicators", "domain", "shared"},
    "composition": {"indicators", "analysis", "regime", "shared"},
    "strategy": {"analysis", "regime", "composition", "shared", "backtest"},
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


def imported_modules(tree: ast.AST, current_module: str) -> set[str]:
    modules: set[str] = set()
    current_parts = current_module.split(".")
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(
                alias.name for alias in node.names if alias.name.split(".", 1)[0] in SOURCE_ROOTS
            )
            continue
        if not isinstance(node, ast.ImportFrom):
            continue
        if node.level:
            prefix = current_parts[: -node.level]
            if node.module:
                target = prefix + node.module.split(".")
            else:
                target = prefix
            module = ".".join(target)
        else:
            module = node.module or ""
        if module and module.split(".", 1)[0] in SOURCE_ROOTS:
            modules.add(module)
    return modules


def main() -> int:
    failures: list[str] = []
    layer_graph: dict[str, set[str]] = {}
    file_graph: dict[Path, set[Path]] = {}

    for path in sorted(ROOT.rglob("*.py")):
        layer = layer_of(path)
        if layer is None:
            continue
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(path))
        except SyntaxError as exc:
            failures.append(f"{path}: syntax error: {exc}")
            continue

        raw_header = re.match(r"^\"\"\"(.*?)\"\"\"", source, re.DOTALL)
        raw_doc = raw_header.group(1).lstrip("\n") if raw_header else ""
        doc = ast.get_docstring(tree, clean=False)
        header, ordered = parse_header(raw_doc or doc or "")
        if ordered != list(HEADER_FIELDS):
            failures.append(f"{path}: non-canonical header field order/schema")
        if header.get("FILE") != path.relative_to(ROOT).as_posix():
            failures.append(f"{path}: FILE header does not match repository path")
        for key in HEADER_FIELDS:
            if not header.get(key):
                failures.append(f"{path}: missing {key}")
        if header.get("LAYER") != layer:
            failures.append(f"{path}: declared LAYER={header.get('LAYER')!r}, expected {layer!r}")
        if not header.get("RESPONSIBILITY"):
            failures.append(f"{path}: missing RESPONSIBILITY")
        if not header.get("OWNS"):
            failures.append(f"{path}: missing OWNS")
        if not header.get("DOES_NOT_OWN"):
            failures.append(f"{path}: missing DOES_NOT_OWN")

        imported = imported_project_layers(tree)
        declared = declared_project_dependencies(header.get("DEPENDENCIES", ""))
        # Same-layer imports remain valid declared/file-level dependencies.
        # Only the cross-layer architecture graph excludes the current layer.
        if imported != declared:
            failures.append(
                f"{path}: DEPENDENCIES mismatch; declared={sorted(declared)}, actual={sorted(imported)}"
            )

        cross_layer_imported = imported - {layer}
        layer_graph.setdefault(layer, set()).update(cross_layer_imported)
        bad = {target for target in cross_layer_imported if not dependency_allowed(layer, target)}
        for bad_target in sorted(bad):
            failures.append(f"{path}: forbidden dependency {layer} -> {bad_target}")

        source_module = module_name_for(path)
        file_graph.setdefault(path, set())
        for module in imported_modules(tree, source_module):
            target_path = resolve_module(module)
            if target_path is not None and target_path != path:
                file_graph[path].add(target_path)

    def find_cycles(graph: dict[Path, set[Path]]) -> list[str]:
        failures_local: list[str] = []
        visiting: set[Path] = set()
        visited: set[Path] = set()

        def visit(node: Path, stack: list[Path]) -> None:
            if node in visiting:
                cycle = stack[stack.index(node) :] + [node] if node in stack else stack + [node]
                failures_local.append("dependency cycle: " + " -> ".join(map(str, cycle)))
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
        return failures_local

    failures.extend(find_cycles(file_graph))
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
