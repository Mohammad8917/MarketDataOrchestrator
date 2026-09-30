"""Verify compliance registry contract counting excludes the table header."""

import re

from validation.compliance_registry_validator import CONTRACTS


def test_contract_registry_count_excludes_header() -> None:
    text = CONTRACTS.read_text(encoding="utf-8")
    contract_ids = re.findall(
        r"^\| (?!contract_id\b)([a-z0-9_]+) \|",
        text,
        re.MULTILINE,
    )

    assert len(contract_ids) == 15
    assert len(contract_ids) == len(set(contract_ids))
    assert "contract_id" not in contract_ids
