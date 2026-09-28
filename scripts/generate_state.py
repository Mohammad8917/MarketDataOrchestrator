#!/usr/bin/env python3
"""Fully automatic PROJECT_STATE.md generator."""

import json
import re
import subprocess  # nosec
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATES = [f"G{i:02d}" for i in range(1, 8)]

PRODUCT_FILES = (
    ("MarketDataEvent", "domain/market_data_event.py"),
    ("MarketDataStore", "persistence/market_data_store.py"),
    ("SimpleBacktestEngine", "backtest/engine.py"),
    ("EquityCurveData", "shared/contracts/equity_curve.py"),
    ("BinanceProvider", "ingestion/providers/binance_provider.py"),
    ("MarketBar", "shared/contracts/market_bar.py"),
    ("DonchianStrategy", "strategy/trend/donchian.py"),
    ("StrategyBacktestEngine", "backtest/strategy_engine.py"),
    ("PerformanceMetrics", "strategy/evaluation/performance_metrics.py"),
)


def run(cmd, check=False):
    try:
        return subprocess.check_output(  # nosec
            cmd,
            text=True,
            stderr=subprocess.DEVNULL,
            cwd=ROOT,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "" if not check else None


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def git_state():
    source_sha = __import__("os").environ.get("STATE_SOURCE_SHA") or run(
        ["git", "rev-parse", "HEAD"]
    )
    return {
        "branch": run(["git", "branch", "--show-current"]) or "DETACHED",
        "sha": source_sha or "UNKNOWN",
        "sha_short": run(["git", "rev-parse", "--short", source_sha]) or "UNKNOWN",
        "last_msg": run(["git", "log", "-1", "--format=%s", source_sha]) or "UNKNOWN",
        "last_date": run(["git", "log", "-1", "--format=%ci", source_sha]) or "UNKNOWN",
    }


def sha_history():
    raw = run(["git", "log", "--format=%H|%s|%ci", "-20"])
    if not raw:
        return []

    ci_dir = ROOT / "evidence" / "sha_status"
    ci_map = {}
    if ci_dir.exists():
        for path in ci_dir.glob("*.json"):
            data = load_json(path)
            if isinstance(data, dict) and data.get("sha"):
                ci_map[data["sha"]] = data

    history = []
    for line in raw.splitlines():
        parts = line.split("|", 2)
        if len(parts) != 3:
            continue
        sha, msg, date = parts
        entry = ci_map.get(sha, {})
        history.append(
            {
                "sha": sha[:8],
                "status": entry.get("status", "UNKNOWN"),
                "note": msg[:80],
                "date": date.split(" ")[0],
            }
        )
    return history


def adr_index():
    adr_dir = ROOT / "docs" / "adr"
    if not adr_dir.exists():
        return []

    adrs = []
    for path in sorted(adr_dir.glob("*.md")):
        content = path.read_text(encoding="utf-8", errors="ignore")
        match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        title = match.group(1).strip() if match else path.stem
        adrs.append({"file": path.name, "title": title})
    return adrs


def gaps():
    for path in (
        ROOT / "docs" / "GAP_REGISTER.md",
        ROOT / "docs" / "gap-register.md",
    ):
        if path.exists():
            content = path.read_text(encoding="utf-8", errors="ignore")
            return re.findall(r"(GAP-\d+[^\n]{0,120})", content)
    return []


def gates():
    current_sha = __import__("os").environ.get("STATE_SOURCE_SHA") or run(
        ["git", "rev-parse", "HEAD"]
    )
    status_path = ROOT / "evidence" / "sha_status" / f"{current_sha}.json"
    if status_path.exists():
        data = load_json(status_path)
        if isinstance(data, dict) and data.get("sha") == current_sha:
            gate_data = data.get("gates", {})
            return {gate: gate_data.get(gate, "PENDING") for gate in GATES}

    return {gate: "PENDING" for gate in GATES}


def current_phase_from_commits():
    raw = run(["git", "log", "--format=%s", "-10"])
    keywords = {
        "reconcile": "Reconciliation",
        "baseline": "Baseline",
        "bollinger": "Indicator hardening",
        "skeleton": "Skeleton elimination",
        "ci:": "CI work",
        "adr": "ADR work",
        "donchian": "Donchian vertical slice",
        "strategy": "Strategy vertical slice",
        "performance": "Performance evaluation",
    }
    for line in raw.splitlines():
        low = line.lower()
        for key, phase in keywords.items():
            if key in low:
                return phase
    return "Product development"


def product_surface_markdown():
    lines = [
        "## Current executable product surface (auto)",
        "",
        "Only files present on the checked-out SHA are listed as implemented surface.",
        "",
        "| Capability | File | Present on this SHA |",
        "|---|---|---|",
    ]
    for name, relative_path in PRODUCT_FILES:
        present = (ROOT / relative_path).exists()
        status = "YES" if present else "NO"
        lines.append(f"| {name} | {relative_path} | {status} |")
    return lines


def manual_notes_auto():
    raw = run(["git", "log", "--format=%s", "-10"])
    commits = raw.splitlines() if raw else []
    adr_dir = ROOT / "docs" / "adr"
    recent_adrs = []
    if adr_dir.exists():
        files = sorted(
            adr_dir.glob("*.md"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        recent_adrs = [p.stem for p in files[:5]]

    lines = ["## Recent Commits (auto)"]
    lines.extend(f"- {c}" for c in commits[:5])
    lines.extend(["", "## Recent ADRs (auto)"])
    lines.extend(f"- {a}" for a in recent_adrs)
    return "\n".join(lines)


def gap_summary():
    path = ROOT / "docs" / "GAP_REGISTER.md"
    if not path.exists():
        return {"OPEN": 0, "RESOLVED": 0, "OTHER": 0}

    content = path.read_text(encoding="utf-8", errors="ignore")
    statuses = re.findall(r"^\*\*Status:\*\*\s+(.+)$", content, re.MULTILINE)
    summary = {"OPEN": 0, "RESOLVED": 0, "OTHER": 0}
    for status in statuses:
        upper = status.upper()
        if upper.startswith("RESOLVED"):
            summary["RESOLVED"] += 1
        elif upper.startswith("OPEN"):
            summary["OPEN"] += 1
        else:
            summary["OTHER"] += 1
    return summary


def active_prs():
    import os

    token = os.environ.get("GH_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not token or not repo:
        return ["Unavailable outside GitHub Actions"]
    raw = run(
        [
            "gh",
            "api",
            f"repos/{repo}/pulls?state=open&base=main&per_page=50",
        ]
    )
    if not raw:
        return ["No open PRs targeting main"]
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return ["Unable to resolve open PRs"]
    return [
        f"PR #{item['number']} — {item['title']} — {item['head']['sha'][:8]}"
        for item in data
        if isinstance(item, dict) and item.get("number") and item.get("head", {}).get("sha")
    ] or ["No open PRs targeting main"]


def visitor_status_markdown(git, gate_state, gap_state, phase):
    lines = [
        "# Current Project Status",
        "",
        "> AUTO-GENERATED. DO NOT EDIT.",
        f"> Exact SHA: {git['sha']}",
        f"> Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "## Canonical State",
        "",
        f"- Branch: {git['branch']}",
        f"- Phase: {phase}",
        "",
        "## G01–G07",
        "",
        "| Gate | Status |",
        "|---|---|",
    ]
    lines.extend(f"| {gate} | {gate_state[gate]} |" for gate in GATES)
    lines.extend(
        [
            "",
            "## Findings",
            "",
            f"- Open: **{gap_state['OPEN']}**",
            f"- Resolved: **{gap_state['RESOLVED']}**",
            f"- Other/unclassified: **{gap_state['OTHER']}**",
            "",
            "## Active product surface",
            "",
        ]
    )
    lines.extend(product_surface_markdown()[3:])
    lines.extend(["", "## Open pull requests targeting main", ""])
    lines.extend(f"- {item}" for item in active_prs())
    lines.extend(
        [
            "",
            "## Interpretation rules",
            "",
            "- This page is generated from the exact checked-out SHA.",
            "- A gate is considered passed only when machine evidence for this SHA records SUCCESS.",
            "- PENDING is not treated as success.",
            "- Open PRs are proposals and are not part of main until merged.",
            "- This status page never overrides GitHub Actions evidence.",
            "",
        ]
    )
    return "\n".join(lines)


def interface_chain():
    path = ROOT / "docs" / "contracts.md"
    if not path.exists():
        return "(no contracts.md)"

    content = path.read_text(encoding="utf-8", errors="ignore")
    fence = chr(96) * 3
    match = re.search(
        rf"{fence}\s*\n(.*?)\n{fence}",
        content,
        re.DOTALL,
    )
    return match.group(1).strip()[:500] if match else "(no chain found)"


def generate():
    git = git_state()
    history = sha_history()
    adrs = adr_index()
    gap_list = gaps()
    gate_state = gates()
    phase = current_phase_from_commits()
    notes = manual_notes_auto()
    chain = interface_chain()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    out = [
        "# PROJECT_STATE.md",
        "",
        "> AUTO-GENERATED. DO NOT EDIT.",
        f"> Generated: {now}",
        "> Source: git log + evidence/ + docs/adr/",
        "> WARNING: This file is a diagnostic snapshot, not the canonical source of truth.",
        "> PENDING means no exact-SHA gate evidence is recorded in evidence/sha_status; it does not by itself mean the gate failed.",
        "> For current truth, verify main and the exact commit SHA against GitHub Actions evidence.",
        "",
        "---",
        "",
        "## 1. Current State",
        "",
        f"- Branch: {git['branch']}",
        f"- SHA: {git['sha']}",
        f"- Short: {git['sha_short']}",
        f"- Last commit: {git['last_msg']}",
        f"- Date: {git['last_date']}",
        f"- Phase (auto): {phase}",
        "",
        "## 2. Gate Status",
        "",
    ]

    for gate in GATES:
        status = gate_state[gate]
        out.append(f"- {gate}: {status}")

    out.extend(["", "## 3. ADR Index", ""])
    out.extend(f"- {a['file']} — {a['title']}" for a in adrs)
    out.extend(["", "## 4. Open Gaps", ""])
    out.extend(f"- {g}" for g in gap_list[:30])
    out.extend(["", "## 5. Recent SHA History (auto)", ""])
    out.extend(f"- {e['sha']} — {e['status']} — {e['date']} — {e['note']}" for e in history[:15])

    fence = chr(96) * 3
    out.extend(
        [
            "",
            "## 6. Interface Chain",
            "",
            fence,
            chain,
            fence,
            "",
        ]
    )
    out.extend(product_surface_markdown())
    out.extend(
        [
            "",
            "## 7. Auto Notes",
            "",
            notes,
            "",
            "---",
            "",
            "## 8. Instructions for New Chat",
            "",
            "1. Read this file completely.",
            "2. Answer these 5 questions BEFORE proposing anything:",
            "   - What branch and SHA?",
            "   - What is the gate status?",
            "   - What are 3 open findings?",
            "   - What are 3 next steps?",
            "   - What is the interface chain?",
            "3. Do NOT propose until answered.",
            "",
            "## 9. Locked Principles",
            "",
            "1. README locked.",
            "2. No artificial green gates.",
            "3. Every new SHA restarts G01.",
            "4. Every claim needs machine evidence.",
            "5. Fail-closed: red gate = stop.",
            "6. Consumer before contract (ADR-0014).",
            "7. Interface-First (ADR-0014).",
            "8. Vertical slice before horizontal.",
            "9. No artificial implementation.",
            "",
        ]
    )
    return "\n".join(out)


if __name__ == "__main__":
    git = git_state()
    gate_state = gates()
    gap_state = gap_summary()
    phase = current_phase_from_commits()
    (ROOT / "PROJECT_STATE.md").write_text(generate(), encoding="utf-8")
    (ROOT / "docs" / "STATUS.md").write_text(
        visitor_status_markdown(git, gate_state, gap_state, phase),
        encoding="utf-8",
    )
    print("PROJECT_STATE.md and docs/STATUS.md updated.")
