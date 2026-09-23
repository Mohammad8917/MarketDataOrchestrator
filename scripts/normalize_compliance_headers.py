"""FILE: scripts/normalize_compliance_headers.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Normalize every Python source-file module header to the canonical 15-field Compliance Kit schema while preserving file-specific ownership evidence.
LAYER: scripts
OWNS: Deterministic migration of legacy structured Python headers to the canonical schema.
DOES_NOT_OWN: Runtime behavior, architecture policy definition, semantic code changes, compliance status approval.
DEPENDENCIES: pathlib, re, sys
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
FIELDS = (
    "FILE", "KIT", "FILE_VERSION", "DATE_GREGORIAN", "DATE_PERSIAN",
    "AUTHOR", "RESPONSIBILITY", "LAYER", "OWNS", "DOES_NOT_OWN",
    "DEPENDENCIES", "PYTHON", "LICENSE", "NOTICE", "COMPLIANCE",
)

def value(header: str, key: str) -> str:
    match = re.search(rf"^{re.escape(key)}\\s*:\\s*(.*)$", header, re.MULTILINE)
    return match.group(1).strip() if match else ""

def canonical(text: str, path: Path) -> bool:
    prefix = text[:4096]
    match = re.match(r'^"""(?P<header>[\\s\\S]*?)\\n"""', prefix)
    if not match:
        return False
    header = match.group("header")
    lines = [line.split(":", 1)[0] for line in header.splitlines() if ":" in line]
    return lines == list(FIELDS) and value(header, "FILE") == path.as_posix()

def normalize(text: str, path: Path) -> str:
    match = re.match(r'^"""(?P<header>[\\s\\S]*?)\\n"""', text)
    if not match:
        raise ValueError(f"{path}: missing module header")
    old = match.group("header")
    required = {
        "RESPONSIBILITY": value(old, "RESPONSIBILITY"),
        "OWNS": value(old, "OWNS"),
        "DOES_NOT_OWN": value(old, "DOES_NOT_OWN") or value(old, "DOES NOT OWN"),
        "DEPENDENCIES": value(old, "DEPENDENCIES"),
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        raise ValueError(f"{path}: missing legacy evidence fields: {', '.join(missing)}")
    layer = value(old, "LAYER") or path.parts[0]
    version = value(old, "VERSION") or value(old, "FILE_VERSION") or "1.0.0"
    author = value(old, "AUTHOR") or "محمد حسن زاده"
    body = text[match.end():]
    header = f'''"""FILE: {path.as_posix()}
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: {version}
DATE_GREGORIAN: 2026-09-24
DATE_PERSIAN: 1405-07-02
AUTHOR: {author}
RESPONSIBILITY: {required["RESPONSIBILITY"]}
LAYER: {layer}
OWNS: {required["OWNS"]}
DOES_NOT_OWN: {required["DOES_NOT_OWN"]}
DEPENDENCIES: {required["DEPENDENCIES"]}
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""
'''
    return header + body

def main() -> int:
    files = sorted(ROOT.rglob("*.py"))
    changed = 0
    failures: list[str] = []
    for path in files:
        if canonical(path.read_text(encoding="utf-8"), path.relative_to(ROOT)):
            continue
        try:
            rel = path.relative_to(ROOT)
            updated = normalize(path.read_text(encoding="utf-8"), rel)
            path.write_text(updated, encoding="utf-8", newline="\n")
            changed += 1
        except Exception as exc:
            failures.append(str(exc))
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}", file=sys.stderr)
        return 1
    print(f"Normalized {changed} Python headers.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
