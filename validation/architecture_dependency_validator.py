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
    "ingestion": {"app", "core", "analysis", "strategy", "decision", "risk"},
    "indicators": {"app", "core", "ingestion", "analysis", "strategy", "decision", "risk"},
    "analysis": {"app", "core", "strategy", "decision", "risk"},
    "regime": {"app", "core", "strategy", "decision", "risk"},
    "composition": {"app", "core", "strategy", "decision", "risk"},
    "strategy": {"app", "core", "decision", "risk"},
    "evidence": {"app", "core", "decision", "risk"},
    "decision": {"app", "core", "risk"},
    "risk": {"app", "core", "strategy", "analysis", "indicators"},
    "persistence": {"app", "core", "analysis", "strategy", "decision", "risk"},
    "feedback": {"app", "core", "analysis", "strategy", "decision", "risk"},
    "output": {"app", "core", "analysis", "strategy", "decision", "risk"},
    "validation": {"app", "core", "analysis", "strategy", "composition", "regime"},
    "backtest": {"app", "core"},
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
    rel = path.relative_to(ROOT)
    if not rel.parts:
        return None
    if rel.parts[0] == TEST_ROOT:
        return TEST_ROOT
    if rel.parts[0] == "scripts":
        return "scripts"
    return rel.parts[0] if rel.parts[0] in SOURCE_ROOTS else None


def parse_header(text: str) -> tuple[dict[str, str], list[str]]:
    header: dict[str, str] = {}
    order: list[str] = []
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if key in HEADER_FIELDS:
            header[key] = value.strip()
            order.append(key)
    return header, order


def imported_project_layers(tree: ast.AST) -> set[str]:
    layers: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".", 1)[0]
                if root in SOURCE_ROOTS:
                    layers.add(root)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root = node.module.split(".", 1)[0]
                if root in SOURCE_ROOTS:
                    layers.add(root)
    return layers


def declared_project_dependencies(value: str) -> set[str]:
    normalized = value.replace(";", ",")
    return {
        token.strip().split(".", 1)[0]
        for token in normalized.split(",")
        if token.strip().split(".", 1)[0] in SOURCE_ROOTS
    }


def dependency_allowed(source: str, target: str) -> bool:
    if target == source:
        return True
    return target in ALLOWED.get(source, set()) and target not in FORBIDDEN.get(source, set())


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
