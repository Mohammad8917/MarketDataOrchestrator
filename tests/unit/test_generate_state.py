"""Tests for automatic visitor-state generation."""

import json
from pathlib import Path

import pytest

import scripts.generate_state as generator


def test_gap_summary_classifies_statuses(tmp_path: Path, monkeypatch) -> None:
    gap_dir = tmp_path / "docs"
    gap_dir.mkdir()
    gap_file = gap_dir / "GAP_REGISTER.md"
    gap_file.write_text(
        """
## GAP-001
**Status:** OPEN — active

## GAP-002
**Status:** RESOLVED (2026-09-28)

## GAP-003
**Status:** REVIEW
""",
        encoding="utf-8",
    )
    monkeypatch.setattr(generator, "ROOT", tmp_path)
    assert generator.gap_summary() == {"OPEN": 1, "RESOLVED": 1, "OTHER": 1}


def test_gap_summary_is_zero_when_register_is_missing(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(generator, "ROOT", tmp_path)
    assert generator.gap_summary() == {"OPEN": 0, "RESOLVED": 0, "OTHER": 0}


def test_visitor_status_contains_exact_sha_all_gates_and_product_surface(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        generator,
        "active_prs",
        lambda: ["PR #99 — Example — abcdef12"],
    )
    git = {"branch": "main", "sha": "a" * 40}
    gates = {f"G{i:02d}": "SUCCESS" for i in range(1, 8)}
    gaps = {"OPEN": 2, "RESOLVED": 8, "OTHER": 0}

    output = generator.visitor_status_markdown(
        git,
        gates,
        gaps,
        "Product development",
    )

    assert f"Latest product commit SHA: {git['sha']}" in output
    for gate in gates:
        assert f"| {gate} | SUCCESS |" in output
    assert "Open: **2**" in output
    assert "Resolved: **8**" in output
    assert "PR #99 — Example — abcdef12" in output
    assert "Active product surface" in output


def test_product_surface_marks_files_from_checked_out_sha(tmp_path: Path, monkeypatch) -> None:
    present = tmp_path / "domain" / "market_data_event.py"
    present.parent.mkdir(parents=True)
    present.write_text("pass\n", encoding="utf-8")
    monkeypatch.setattr(generator, "ROOT", tmp_path)

    output = "\n".join(generator.product_surface_markdown())

    assert "| MarketDataEvent | domain/market_data_event.py | YES |" in output
    assert "| MarketDataStore | persistence/market_data_store.py | NO |" in output


def test_git_state_uses_verified_source_sha(monkeypatch) -> None:
    source_sha = "b" * 40
    monkeypatch.setenv("STATE_SOURCE_SHA", source_sha)

    def fake_run(command, check=False):
        mapping = {
            ("git", "branch", "--show-current"): "main",
            ("git", "rev-parse", "--short", source_sha): "bbbbbbbb",
            ("git", "log", "-1", "--format=%s", source_sha): "verified commit",
            ("git", "log", "-1", "--format=%ci", source_sha): "2026-09-28 13:00:00 +0000",
        }
        return mapping.get(tuple(command), "")

    monkeypatch.setattr(generator, "run", fake_run)

    assert generator.git_state() == {
        "branch": "main",
        "sha": source_sha,
        "sha_short": "bbbbbbbb",
        "last_msg": "verified commit",
        "last_date": "2026-09-28 13:00:00 +0000",
    }


def test_gates_reads_exact_sha_from_github_check_runs(monkeypatch) -> None:
    source_sha = "c" * 40
    monkeypatch.setenv("STATE_SOURCE_SHA", source_sha)
    monkeypatch.setenv("GH_TOKEN", "token")
    monkeypatch.setenv("GITHUB_REPOSITORY", "example/repo")
    payload = {
        "check_runs": [
            {"name": f"G{i:02d}_TEST", "status": "completed", "conclusion": "success"}
            for i in range(1, 8)
        ]
    }
    monkeypatch.setattr(
        generator,
        "run",
        lambda command, check=False: json.dumps(payload) if command[0] == "gh" else "",
    )
    assert generator.gates() == {f"G{i:02d}": "SUCCESS" for i in range(1, 8)}


def test_run_and_load_json_boundaries(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    def fail(*args, **kwargs):
        raise FileNotFoundError

    monkeypatch.setattr(generator.subprocess, "check_output", lambda *args, **kwargs: "ok")
    assert generator.run(["git"]) == "ok"
    monkeypatch.setattr(generator.subprocess, "check_output", fail)
    assert generator.run(["missing"]) == ""
    assert generator.run(["missing"], check=True) is None

    bad = tmp_path / "bad.json"
    bad.write_text("{", encoding="utf-8")
    assert generator.load_json(bad) is None
    assert generator.load_json(tmp_path / "missing.json") is None


def test_sha_history_uses_matching_evidence_and_skips_malformed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    evidence = tmp_path / "evidence" / "sha_status"
    evidence.mkdir(parents=True)
    (evidence / "abcdef.json").write_text(
        json.dumps({"sha": "abcdef", "status": "PASS"}), encoding="utf-8"
    )
    monkeypatch.setattr(generator, "ROOT", tmp_path)
    monkeypatch.setattr(
        generator,
        "run",
        lambda command, check=False: "abcdef|subject|2026-10-03 12:00:00 +0000\nbad",
    )
    assert generator.sha_history() == [
        {"sha": "abcdef", "status": "PASS", "note": "subject", "date": "2026-10-03"}
    ]


def test_adr_index_uses_filename_when_heading_is_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    adr_dir = tmp_path / "docs" / "adr"
    adr_dir.mkdir(parents=True)
    (adr_dir / "001.md").write_text("# Decision\n", encoding="utf-8")
    (adr_dir / "002.md").write_text("no heading\n", encoding="utf-8")
    monkeypatch.setattr(generator, "ROOT", tmp_path)
    assert generator.adr_index() == [
        {"file": "001.md", "title": "Decision"},
        {"file": "002.md", "title": "002"},
    ]


def test_gate_helpers_and_evidence_fallback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert (
        generator._gate_from_check_run(
            {"name": "G01_FORMAT_LINT", "status": "queued", "conclusion": "success"}
        )
        is None
    )
    assert (
        generator._gate_from_check_run(
            {"name": 1, "status": "completed", "conclusion": "success"}
        )
        is None
    )
    assert generator._check_run_gate_statuses({"check_runs": []}) is None
    assert generator._check_run_gate_statuses(
        {"check_runs": [{"name": "G02_TYPECHECK", "status": "completed", "conclusion": "failure"}]}
    ) == {"G02": "FAILURE"}
    assert generator._normalize_gate_data({"G01": "PASS", "G02": "FAIL"})["G01"] == "SUCCESS"

    status_dir = tmp_path / "evidence" / "sha_status"
    status_dir.mkdir(parents=True)
    (status_dir / "sha.json").write_text(
        json.dumps({"sha": "sha", "gates": {"G01": "PASS"}}), encoding="utf-8"
    )
    monkeypatch.setattr(generator, "ROOT", tmp_path)
    assert generator._evidence_gate_statuses("sha")["G01"] == "SUCCESS"
    assert generator._evidence_gate_statuses("other") is None


def test_current_phase_and_interface_chain(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(generator, "run", lambda command, check=False: "feat: strategy slice")
    assert generator.current_phase_from_commits() == "Strategy vertical slice"
    monkeypatch.setattr(generator, "run", lambda command, check=False: "")
    assert generator.current_phase_from_commits() == "Product development"

    monkeypatch.setattr(generator, "ROOT", tmp_path)
    assert generator.interface_chain() == "(no contracts.md)"
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "contracts.md").write_text(
        chr(96) * 3 + "\nA -> B\n" + chr(96) * 3 + "\n", encoding="utf-8"
    )
    assert generator.interface_chain() == "A -> B"


def test_active_prs_fallbacks(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)
    assert generator.active_prs() == ["Unavailable outside GitHub Actions"]
    monkeypatch.setenv("GH_TOKEN", "token")
    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")
    monkeypatch.setattr(generator, "run", lambda command, check=False: "")
    assert generator.active_prs() == ["No open PRs targeting main"]
    monkeypatch.setattr(generator, "run", lambda command, check=False: "{")
    assert generator.active_prs() == ["Unable to resolve open PRs"]


def test_generate_builds_complete_snapshot(monkeypatch: pytest.MonkeyPatch) -> None:
    git = {
        "branch": "main",
        "sha": "a" * 40,
        "sha_short": "aaaaaaaa",
        "last_msg": "msg",
        "last_date": "date",
    }
    gates = {gate: "SUCCESS" for gate in generator.GATES}
    monkeypatch.setattr(generator, "git_state", lambda: git)
    monkeypatch.setattr(generator, "sha_history", lambda: [])
    monkeypatch.setattr(generator, "adr_index", lambda: [])
    monkeypatch.setattr(generator, "gaps", lambda: [])
    monkeypatch.setattr(generator, "gates", lambda: gates)
    monkeypatch.setattr(generator, "current_phase_from_commits", lambda: "Product development")
    monkeypatch.setattr(generator, "manual_notes_auto", lambda: "notes")
    monkeypatch.setattr(generator, "interface_chain", lambda: "chain")
    assert "# PROJECT_STATE.md" in generator.generate()
    assert "## 6. Interface Chain" in generator.generate()
