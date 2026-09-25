"""
FILE: validation/markdown_registry.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-25
DATE_PERSIAN: 1405-07-03
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Provide shared, section-scoped Markdown table extraction for registry validators
LAYER: validation
OWNS: Shared Markdown registry parsing semantics
DOES_NOT_OWN: Registry policy, contract ownership, runtime behavior
DEPENDENCIES: stdlib
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

from pathlib import Path
import re

_CONTRACT_ID_ROW = re.compile(r"^\| ([a-z0-9_]+) \|", re.MULTILINE)


def extract_contract_ids_from_md(path: Path, section: str) -> list[str]:
    """Extract contract IDs from one Markdown table section, excluding its header."""
    text = path.read_text(encoding="utf-8")
    marker = f"## {section}"
    if marker not in text:
        raise ValueError(f"Markdown section not found: {section!r}")

    section_text = text.split(marker, 1)[1]
    next_section = re.search(r"^##\s+", section_text, re.MULTILINE)
    if next_section is not None:
        section_text = section_text[: next_section.start()]

    rows = _CONTRACT_ID_ROW.findall(section_text)
    return rows[1:]
