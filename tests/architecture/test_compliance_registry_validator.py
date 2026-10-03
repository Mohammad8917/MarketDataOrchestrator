"""Verify compliance registry contract counting excludes the table header."""

import re
from pathlib import Path

from validation import compliance_registry_validator as validator
from validation.compliance_registry_validator import CONTRACTS


def test_contract_registry_count_excludes_header() -> None:
    text = CONTRACTS.read_text(encoding="utf-8")
    contract_ids = re.findall(
        r"^\| (?!contract_id\b)([a-z0-9_]+) \|",
        text,
        re.MULTILINE,
    )

    assert len(contract_ids) == 35
    assert len(contract_ids) == len(set(contract_ids))
    assert "contract_id" not in contract_ids


def test_main_passes_canonical_registry() -> None:
    assert validator.main() == 0


def test_main_fails_when_canonical_registry_is_missing(monkeypatch) -> None:
    missing = validator.ROOT / "missing-compliance-registry.md"
    monkeypatch.setattr(validator, "COMPLIANCE", missing)
    assert validator.main() == 1


def test_main_fails_for_duplicate_control_ids(monkeypatch, tmp_path) -> None:
    compliance = tmp_path / "README.md"
    compliance.write_text(
        "| C1_TEST | value |\\n| C1_TEST | value |\\n| G01_FORMAT_LINT | value |\\n",
        encoding="utf-8",
    )
    contracts = tmp_path / "contracts.md"
    contracts.write_text("| contract_id | value |\\n| test_contract | value |\\n", encoding="utf-8")
    capabilities = tmp_path / "capability-matrix.md"
    capabilities.write_text(
        "".join(f"| rate_{i} | value |\\n" for i in range(15)),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "COMPLIANCE", compliance)
    monkeypatch.setattr(validator, "CONTRACTS", contracts)
    monkeypatch.setattr(validator, "CAPABILITIES", capabilities)
    assert validator.main() == 1


def _write_valid_registry_inputs(tmp_path: Path) -> tuple[Path, Path, Path]:
    compliance = tmp_path / "README.md"
    gates = sorted(validator.GATES)
    compliance.write_text(
        "| C1_TEST | value |\\n"
        + "".join(f"| {gate} | value |\\n" for gate in gates)
        + "| A | APP-A-1 | G01_FORMAT_LINT |\\n",
        encoding="utf-8",
    )
    contracts = tmp_path / "contracts.md"
    contracts.write_text(
        "| contract_id | value |\\n| test_contract | value |\\n",
        encoding="utf-8",
    )
    capabilities = tmp_path / "capability-matrix.md"
    capabilities.write_text(
        "".join(f"| rate_{i} | value |\\n" for i in range(15)),
        encoding="utf-8",
    )
    return compliance, contracts, capabilities


def test_main_fails_when_mandatory_gate_set_is_incomplete(
    monkeypatch, tmp_path
) -> None:
    compliance, contracts, capabilities = _write_valid_registry_inputs(tmp_path)
    compliance.write_text(
        compliance.read_text(encoding="utf-8").replace(
            "| G08_RELEASE_VERIFICATION | value |\\n", ""
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "COMPLIANCE", compliance)
    monkeypatch.setattr(validator, "CONTRACTS", contracts)
    monkeypatch.setattr(validator, "CAPABILITIES", capabilities)
    assert validator.main() == 1


def test_main_fails_when_appendix_references_unknown_gate(
    monkeypatch, tmp_path
) -> None:
    compliance, contracts, capabilities = _write_valid_registry_inputs(tmp_path)
    compliance.write_text(
        compliance.read_text(encoding="utf-8").replace(
            "| A | APP-A-1 | G01_FORMAT_LINT |",
            "| A | APP-A-1 | G99_UNKNOWN_GATE |",
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "COMPLIANCE", compliance)
    monkeypatch.setattr(validator, "CONTRACTS", contracts)
    monkeypatch.setattr(validator, "CAPABILITIES", capabilities)
    assert validator.main() == 1


def test_main_fails_when_contract_or_rate_baseline_is_incomplete(
    monkeypatch, tmp_path
) -> None:
    compliance, contracts, capabilities = _write_valid_registry_inputs(tmp_path)
    contracts.write_text("| contract_id | value |\\n", encoding="utf-8")
    capabilities.write_text("| rate_1 | value |\\n", encoding="utf-8")
    monkeypatch.setattr(validator, "COMPLIANCE", compliance)
    monkeypatch.setattr(validator, "CONTRACTS", contracts)
    monkeypatch.setattr(validator, "CAPABILITIES", capabilities)
    assert validator.main() == 1
