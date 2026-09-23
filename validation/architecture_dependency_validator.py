"""Architecture dependency and cycle validator.

Validates Python source ownership headers and the frozen layer dependency direction.
This validator is intentionally fail-closed: an unknown layer, malformed declaration,
forbidden cross-layer import, or detected cycle is a failure.
"""

from __future__ import annotations

import ast
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOTS = {
    "analysis", "backtest", "composition", "config", "core", "decision",
    "domain", "domain_adapters", "evidence", "feedback", "indicators",
    "ingestion", "output", "persistence", "regime", "risk", "shared",
    "strategy", "validation", "app",
}

ALLOWED = {
    "app": {"core", "config", "shared"},
    "core": {"config", "shared", "ingestion", "persistence", "validation", "output"},
    "config": {"shared"},
    "shared": {"shared"},
    "domain": {"shared"},
    "ingestion": {"shared", "config", "domain", "ingestion"},
    "domain_adapters": {"domain", "ingestion", "shared"},
    "indicators": {"shared", "domain"},
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
    "backtest": {
        "ingestion", "indicators", "analysis", "regime", "composition",
        "strategy", "evidence", "decision", "risk", "validation", "shared",
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
}

def layer_of(path: Path) -> str | None:
    parts = path.relative_to(ROOT).parts
    return parts[0] if parts and parts[0] in SOURCE_ROOTS else None

def imported_layers(tree: ast.AST) -> set[str]:
    layers: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = node.names
        elif isinstance(node, ast.ImportFrom):
            names = node.names
            if node.level:
                continue
        else:
            continue
        for alias in names:
            root = alias.name.split(".", 1)[0]
            if root in SOURCE_ROOTS:
                layers.add(root)
    return layers

def parse_header(doc: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in doc.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if key in {"RESPONSIBILITY", "LAYER", "OWNS", "DOES NOT OWN", "DEPENDENCIES"}:
            out[key] = value.strip()
    return out

def main() -> int:
    failures: list[str] = []
    graph: dict[str, set[str]] = {}

    for path in sorted(ROOT.rglob("*.py")):
        layer = layer_of(path)
        if layer is None:
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            failures.append(f"{path}: syntax error: {exc}")
            continue

        doc = ast.get_docstring(tree, clean=False) or ""
        header = parse_header(doc)
        if header.get("LAYER") != layer:
            failures.append(f"{path}: declared LAYER={header.get('LAYER')!r}, expected {layer!r}")
        if not header.get("RESPONSIBILITY"):
            failures.append(f"{path}: missing RESPONSIBILITY")
        if not header.get("OWNS"):
            failures.append(f"{path}: missing OWNS")
        if not header.get("DOES NOT OWN"):
            failures.append(f"{path}: missing DOES NOT OWN")

        imported = imported_layers(tree)
        graph.setdefault(layer, set()).update(imported)
        bad = (imported & FORBIDDEN.get(layer, set())) | (imported - ALLOWED.get(layer, set()))
        for target in sorted(bad):
            failures.append(f"{path}: forbidden dependency {layer} -> {target}")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str, stack: list[str]) -> None:
        if node in visiting:
            failures.append("dependency cycle: " + " -> ".join(stack + [node]))
            return
        if node in visited:
            return
        visiting.add(node)
        for target in sorted(graph.get(node, set())):
            visit(target, stack + [node])
        visiting.remove(node)
        visited.add(node)

    for node in sorted(graph):
        visit(node, [])

    if failures:
        print("ARCHITECTURE DEPENDENCY: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("ARCHITECTURE DEPENDENCY: PASS")
    print(f"- layers scanned: {len(graph)}")
    print(f"- dependency edges: {sum(len(v) for v in graph.values())}")
    print("- cycles: none")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
