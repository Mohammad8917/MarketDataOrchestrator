"""FILE: tests/unit/test_repository_truth.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-01
DATE_PERSIAN: 1405-07-09
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Verify repository truth synchronization helpers and generated visitor-state invariants.
LAYER: tests
OWNS: Focused tests for repository truth synchronization behavior.
DOES_NOT_OWN: Production implementation, CI gate semantics, provider runtime behavior.
DEPENDENCIES: pytest, scripts.repository_truth
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from pathlib import Path

from scripts.repository_truth import canonical_source_sha, exchanges, roadmap, sync_readme


def test_exchange_inventory_contains_fifteen_targets() -> None:
    rows = exchanges()
    assert len(rows) == 15
    assert rows[0] == ("Binance", "implemented", "1")
    assert rows[-1][2] == "15"


def test_roadmap_reports_inventory_count() -> None:
    text = roadmap()
    assert "Provider target — 15" in text
    assert "Implemented: 1/15" in text
    assert "| 1 | Binance | implemented |" in text


def test_readme_live_status_is_inserted_once(tmp_path: Path, monkeypatch) -> None:
    readme = tmp_path / "README.md"
    readme.write_text(
        "**Architecture-first trading-system foundation — product first, compliance as a guardrail.**\n",
        encoding="utf-8",
    )
    monkeypatch.setattr("scripts.repository_truth.ROOT", tmp_path)
    (tmp_path / "README.md").write_text(
        "**Architecture-first trading-system foundation — product first, compliance as a guardrail.**\n",
        encoding="utf-8",
    )
    block = sync_readme(
        {"branch": "main", "sha": "abc", "subject": "test", "committed": "2026-10-01T00:00:00Z"},
        {f"G{i:02d}": "SUCCESS" for i in range(1, 8)},
        [("Demo", "demo.py")],
    )
    assert block.count("LIVE-STATUS:START") == 1
    assert block.count("LIVE-STATUS:END") == 1
    assert "PENDING = no completed exact-SHA evidence yet" in block


def test_readme_live_status_replaces_previous_block(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("scripts.repository_truth.ROOT", tmp_path)
    (tmp_path / "README.md").write_text(
        "<!-- LIVE-STATUS:START -->\nold\n<!-- LIVE-STATUS:END -->\n",
        encoding="utf-8",
    )
    result = sync_readme(
        {"branch": "main", "sha": "new", "subject": "test", "committed": "2026-10-01T00:00:00Z"},
        {f"G{i:02d}": "SUCCESS" for i in range(1, 8)},
        [],
    )
    assert "old" not in result
    assert "- Latest product commit SHA: new" in result


def test_canonical_source_skips_visitor_generated_commits(monkeypatch) -> None:
    history = "\n".join(
        [
            "gen-3|chore: synchronize visitor changelog [skip ci]",
            "gen-2|chore: synchronize visitor README status [skip ci]",
            "gen-1|chore: synchronize visitor status snapshot [skip ci]",
            "source-1|fix: real product change",
        ]
    )

    def fake_run(*args: str) -> str:
        if args[:2] == ("git", "log"):
            return history
        if args[:3] == ("git", "rev-parse", "HEAD"):
            return "head"
        raise AssertionError(args)

    monkeypatch.setattr("scripts.repository_truth.run", fake_run)
    assert canonical_source_sha() == "source-1"


def test_visitor_quick_start_declares_ci_complete_test_dependencies() -> None:
    root = Path(__file__).resolve().parents[2]
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
    readme = (root / "README.md").read_text(encoding="utf-8")

    assert '"pytest-asyncio>=1.4,<2"' in pyproject
    assert '"coverage>=7.0,<8"' in pyproject
    assert "python -m pip install -r constraints-ci.txt" in readme
    assert "pip install -e '.[test]'" not in readme


def test_visitor_backtest_command_is_self_contained() -> None:
    root = Path(__file__).resolve().parents[2]
    script = (root / "scripts" / "run_backtest.py").read_text(encoding="utf-8")

    assert "ROOT = Path(__file__).resolve().parents[1]" in script
    assert "sys.path.insert(0, str(ROOT))" in script
    assert "PYTHONPATH" not in script


def test_repository_truth_sync_is_burst_and_race_hardened() -> None:
    root = Path(__file__).resolve().parents[2]
    workflow = (root / ".github" / "workflows" / "repository-truth-sync.yml").read_text(
        encoding="utf-8"
    )

    assert "cancel-in-progress: true" in workflow
    assert "for attempt in 1 2 3 4 5; do" in workflow
    assert "git fetch origin main" in workflow
    assert "git reset --hard origin/main" in workflow
    assert "git push origin HEAD:main" in workflow
    assert 'test "$(git rev-parse origin/main)" = "$(git rev-parse HEAD)"' in workflow
    assert (
        "Concurrent main update detected; retrying synchronization (attempt $attempt/5)."
        in workflow
    )
