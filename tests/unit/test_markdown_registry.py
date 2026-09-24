"""
FILE: tests/unit/test_markdown_registry.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-09-25
DATE_PERSIAN: 1405-07-03
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Regression-test section-scoped Markdown contract ID extraction
LAYER: tests
OWNS: Regression assertions for shared Markdown registry parsing
DOES_NOT_OWN: Registry policy or parser implementation
DEPENDENCIES: validation.markdown_registry, pytest
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from pathlib import Path

import pytest

from validation.markdown_registry import extract_contract_ids_from_md


def test_extract_contract_ids_skips_header_and_stays_in_named_section(
    tmp_path: Path,
) -> None:
    path = tmp_path / "contracts.md"
    path.write_text(
        "# Registry\n\n"
        "## Initial contract baseline\n\n"
        "| contract_id | owner_layer | status |\n"
        "|---|---|---|\n"
        "| market_data_event | domain | ACTIVE |\n"
        "| equity_curve | shared | ACTIVE |\n\n"
        "## Typed contract bindings\n\n"
        "| contract_id | owner_layer | status |\n"
        "|---|---|---|\n"
        "| shadow_contract | domain | ACTIVE |\n",
        encoding="utf-8",
    )

    assert extract_contract_ids_from_md(path, "Initial contract baseline") == [
        "market_data_event",
        "equity_curve",
    ]


def test_extract_contract_ids_requires_existing_section(tmp_path: Path) -> None:
    path = tmp_path / "contracts.md"
    path.write_text("# Registry\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Markdown section not found"):
        extract_contract_ids_from_md(path, "Initial contract baseline")
