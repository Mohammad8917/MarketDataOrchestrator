"""FILE: scripts/repository_truth.py
KIT: Architecture & Implementation Compliance Kit
FILE_VERSION: 1.0.0
DATE_GREGORIAN: 2026-10-01
DATE_PERSIAN: 1405-07-09
AUTHOR: محمد حسن زاده
RESPONSIBILITY: Synchronize visitor-facing repository documentation from the canonical GitHub main state.
LAYER: scripts
OWNS: Deterministic generation of project information, roadmap, changelog, README live status, and architecture overview.
DOES_NOT_OWN: Product implementation, CI gate semantics, trading decisions, provider runtime behavior.
DEPENDENCIES: datetime, pathlib, re, subprocess
PYTHON: >=3.13
LICENSE: Proprietary — All Rights Reserved
NOTICE: Unauthorized use prohibited without written authorization
COMPLIANCE: Architecture & Implementation Compliance Kit v1.0
"""

from __future__ import annotations

import re
import subprocess  # nosec
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRODUCT_HEADER = "## Current executable product surface (auto)"


def run(*args: str) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()  # nosec


def canonical_source_sha() -> str:
    raw = run("git", "log", "--format=%H|%s", "-50")
    generated_prefixes = (
        "chore: synchronize repository truth",
        "chore: reconcile unapplied GitHub updates",
        "chore: recover canonical project state",
        "chore: auto-update project state",
    )
    for line in raw.splitlines():
        sha, subject = line.split("|", 1)
        if not subject.startswith(generated_prefixes):
            return sha
    return run("git", "rev-parse", "HEAD")


def current_state() -> dict[str, str]:
    source_sha = canonical_source_sha()
    return {
        "sha": source_sha,
        "branch": "main",
        "subject": run("git", "log", "-1", "--pretty=%s", source_sha),
        "committed": run("git", "log", "-1", "--pretty=%cI", source_sha),
    }


def gates() -> dict[str, str]:
    text = (ROOT / "docs" / "STATUS.md").read_text(encoding="utf-8")
    found = dict(re.findall(r"\| (G0[1-7]) \| (SUCCESS|PENDING|FAIL|SKIPPED) \|", text))
    return {f"G{i:02d}": found.get(f"G{i:02d}", "PENDING") for i in range(1, 8)}


def product_surface() -> list[tuple[str, str]]:
    text = (ROOT / "PROJECT_STATE.md").read_text(encoding="utf-8")
    if PRODUCT_HEADER not in text:
        return []
    section = text.split(PRODUCT_HEADER, 1)[1].split("## 7.", 1)[0]
    return re.findall(r"\| ([^|]+) \| ([^|]+) \| YES \|", section)


def exchanges() -> list[tuple[str, str, str]]:
    path = ROOT / "config" / "exchanges.yaml"
    if not path.exists():
        return []
    rows: list[tuple[str, str, str]] = []
    name = status = priority = ""
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("- name:"):
            if name:
                rows.append((name, status, priority))
            name = line.split(":", 1)[1].strip()
            status = priority = ""
        elif line.startswith("status:"):
            status = line.split(":", 1)[1].strip()
        elif line.startswith("priority:"):
            priority = line.split(":", 1)[1].strip()
    if name:
        rows.append((name, status, priority))
    return rows


def write_if_changed(path: Path, content: str) -> None:
    content = content.rstrip() + "\n"
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def changelog() -> str:
    raw = run("git", "log", "-30", "--date=short", "--pretty=%h|%ad|%s|%an")
    lines = ["# CHANGELOG", "", "> AUTO-GENERATED FROM GIT HISTORY. DO NOT EDIT.", ""]
    for row in raw.splitlines():
        sha, date, subject, author = row.split("|", 3)
        lines.append(f"- {date} — {sha} — {subject} — {author}")
    return "\n".join(lines)


def roadmap() -> str:
    rows = exchanges()
    implemented = sum(status == "implemented" for _, status, _ in rows)
    lines = [
        "# ROADMAP",
        "",
        "> Provider inventory is machine-readable in config/exchanges.yaml.",
        "",
        "## Product direction",
        "",
        "Build the trading-analysis system bottom-up: market data → quality → time alignment → market structure → regime → sensors → setup → confirmation → liquidity/cost/edge → risk → decision → audit → evaluation.",
        "",
        "## Markets",
        "",
        "| Market | Current repository status |",
        "|---|---|",
        "| Crypto | Binance provider implemented; broader provider expansion planned |",
        "| Forex | Architecture target; provider implementation planned |",
        "| Gold | Architecture target; provider implementation planned |",
        "",
        f"## Provider target — {len(rows)}",
        "",
        f"Implemented: {implemented}/{len(rows)}",
        "",
        "| # | Provider | Status |",
        "|---:|---|---|",
    ]
    lines.extend(f"| {priority} | {name} | {status} |" for name, status, priority in rows)
    lines.extend(
        [
            "",
            "## Engineering order",
            "",
            "1. Contract and methodology",
            "2. Strong unit/contract tests",
            "3. Persistence/infrastructure consumer",
            "4. Engine and strategy analysis",
            "5. Evaluation and metrics",
            "6. Application/orchestration",
            "7. Telegram/UI only after lower layers are executable",
            "",
            "## Guardrails",
            "",
            "- No Data Quality → No Analysis.",
            "- No Valid Setup → No Trade.",
            "- No Positive Net Edge → No Trade.",
            "- G01–G07 remain compliance guardrails; they do not replace product development.",
        ]
    )
    return "\n".join(lines)


def project_info(
    state: dict[str, str], gate_state: dict[str, str], surface: list[tuple[str, str]]
) -> str:
    gate_lines = "\n".join(f"- {key}: {value}" for key, value in gate_state.items())
    surface_lines = "\n".join(f"- {name}: {path}" for name, path in surface)
    lines = [
        "# PROJECT INFO",
        "",
        "> AUTO-GENERATED FROM THE CANONICAL CHECKED-OUT STATE.",
        "",
        "## Identity",
        "",
        f"- Branch: {state['branch']}",
        f"- SHA: {state['sha']}",
        f"- Last commit: {state['subject']}",
        f"- Commit time: {state['committed']}",
        f"- Generated from commit time: {state['committed']}",
        "",
        "## Verification",
        "",
        gate_lines,
        "",
        "## Product surface",
        "",
        surface_lines or "- No product surface detected.",
        "",
        "## Architecture direction",
        "",
        "The repository is developed bottom-up and market-agnostic. Crypto, Forex, and Gold are product targets; provider-specific behavior remains behind ingestion boundaries.",
        "",
        "## Canonical rules",
        "",
        "- main is the canonical branch.",
        "- Exact-SHA GitHub Actions evidence is authoritative for gate claims.",
        "- Compliance is a guardrail, not the product objective.",
        "- Strategy code does not own risk, cost, decision, or provider I/O.",
        "",
        "## Important entry points",
        "",
        "- README",
        "- PROJECT_STATE.md",
        "- docs/STATUS.md",
        "- CHANGELOG.md",
        "- ROADMAP.md",
        "- docs/GAP_REGISTER.md",
        "- docs/architecture/overview.md",
        "- CONTRIBUTING.md",
    ]
    return "\n".join(lines)


def architecture_overview() -> str:
    return "\n".join(
        [
            "# Architecture Overview",
            "",
            "## Canonical direction",
            "",
            "Market Data → Data Quality → Time Alignment → Market Structure → Regime/Uncertainty/Volatility → Strategy Sensors → Setup → MTF Confirmation → Liquidity/Cost/Expected Edge → Risk → Decision → Audit/Evaluation",
            "",
            "## Executable foundation",
            "",
            "MarketDataEvent → MarketDataStore → BacktestEngine → Strategy → Evaluation",
            "",
            "## Market rule",
            "",
            "Core contracts remain market-agnostic. Crypto, Forex, and Gold are represented as market contexts rather than separate architecture trees.",
            "",
            "## Product-first rule",
            "",
            "A capability becomes canonical only after contract, methodology, implementation, focused tests, and exact-SHA verification are present.",
        ]
    )


def contributing() -> str:
    return "\n".join(
        [
            "# CONTRIBUTING",
            "",
            "## Development order",
            "",
            "Contract → Domain → Persistence/Infrastructure → Engine → Strategy/Analysis → Application → Orchestrator/UI",
            "",
            "Do not start implementation from Telegram or orchestration.",
            "",
            "## Quality",
            "",
            "Every new Python file has one primary responsibility and is compatible with Python 3.13+.",
            "",
            "## GitHub source of truth",
            "",
            "Changes become canonical only after they are committed to GitHub and merged into main.",
            "",
            "## Verification",
            "",
            "Never weaken, reorder, or bypass G01–G07 to obtain a green result. Claims must be tied to exact-SHA GitHub Actions evidence.",
            "",
            "## Product boundaries",
            "",
            "Strategy sensors describe market conditions. They do not independently emit final BUY/SELL decisions and do not own risk, cost, execution, or provider transport.",
        ]
    )


def sync_readme(
    state: dict[str, str], gate_state: dict[str, str], surface: list[tuple[str, str]]
) -> str:
    path = ROOT / "README.md"
    text = path.read_text(encoding="utf-8")
    gates_text = " · ".join(f"{k}={v}" for k, v in gate_state.items())
    block = "\n".join(
        [
            "<!-- LIVE-STATUS:START -->",
            "## Live project status",
            "",
            f"- Canonical branch: {state['branch']}",
            f"- Exact SHA: {state['sha']}",
            f"- Last commit: {state['subject']}",
            f"- Gates: {gates_text}",
            f"- Executable product capabilities detected: {len(surface)}",
            "- Source of truth: GitHub main + exact-SHA Actions evidence",
            "<!-- LIVE-STATUS:END -->",
        ]
    )
    pattern = r"<!-- LIVE-STATUS:START -->[\s\S]*?<!-- LIVE-STATUS:END -->"
    if re.search(pattern, text):
        return re.sub(pattern, block, text, count=1)
    marker = "**Architecture-first trading-system foundation — product first, compliance as a guardrail.**"
    return text.replace(marker, marker + "\n\n" + block, 1)


def main() -> None:
    state = current_state()
    gate_state = gates()
    surface = product_surface()
    write_if_changed(ROOT / "CHANGELOG.md", changelog())
    write_if_changed(ROOT / "ROADMAP.md", roadmap())
    write_if_changed(ROOT / "PROJECT_INFO.md", project_info(state, gate_state, surface))
    write_if_changed(ROOT / "CONTRIBUTING.md", contributing())
    write_if_changed(ROOT / "docs" / "architecture" / "overview.md", architecture_overview())
    write_if_changed(ROOT / "README.md", sync_readme(state, gate_state, surface))


if __name__ == "__main__":
    main()
