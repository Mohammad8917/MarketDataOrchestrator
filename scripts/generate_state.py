#!/usr/bin/env python3
"""Fully automatic PROJECT_STATE.md generator."""

import json
import re
import subprocess  # nosec
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATES = [f"G{i:02d}" for i in range(1, 8)]


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
    return {
        "branch": run(["git", "branch", "--show-current"]) or "DETACHED",
        "sha": run(["git", "rev-parse", "HEAD"]) or "UNKNOWN",
        "sha_short": run(["git", "rev-parse", "--short", "HEAD"]) or "UNKNOWN",
        "last_msg": run(["git", "log", "-1", "--format=%s"]) or "UNKNOWN",
        "last_date": run(["git", "log", "-1", "--format=%ci"]) or "UNKNOWN",
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
    current_sha = run(["git", "rev-parse", "HEAD"])
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
    }
    for line in raw.splitlines():
        low = line.lower()
        for key, phase in keywords.items():
            if key in low:
                return phase
    return "Unknown"


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


def interface_chain():
    path = ROOT / "docs" / "contracts.md"
    if not path.exists():
        return "(no contracts.md)"

    content = path.read_text(encoding="utf-8", errors="ignore")
    fence = chr(96) * 3
    match = re.search(
        f"{fence}\s*\n(.*?)\n{fence}",
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
    (ROOT / "PROJECT_STATE.md").write_text(generate(), encoding="utf-8")
    print("PROJECT_STATE.md updated.")
