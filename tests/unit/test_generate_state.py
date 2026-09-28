"""Tests for automatic visitor-state generation."""

from pathlib import Path

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

    assert f"Exact SHA: {git['sha']}" in output
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
