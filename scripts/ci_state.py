#!/usr/bin/env python3
"""CI state evidence helpers used by .github/workflows/state.yml."""

from __future__ import annotations

import json
import os
import shutil
import subprocess  # nosec B404 - required for read-only git metadata in CI state generation
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "evidence" / "sha_status"

MAPPING = {
    "G01_FORMAT_LINT": "G01",
    "G02_TYPECHECK": "G02",
    "G03_UNIT_CONTRACT": "G03",
    "G04_ARCHITECTURE_DEPENDENCY": "G04",
    "G05_COVERAGE": "G05",
    "G06_SECURITY_SUPPLY_CHAIN": "G06",
    "G07_INTEGRATION_RESILIENCE": "G07",
}


def collect() -> None:
    jobs_path = Path(os.environ["JOBS_JSON_PATH"])
    target_sha = os.environ["TARGET_SHA"]
    run_id = int(os.environ["EVENT_RUN_ID"] or os.environ["RESOLVED_RUN_ID"])
    jobs = json.loads(jobs_path.read_text(encoding="utf-8"))
    gates = {gate: "PENDING" for gate in MAPPING.values()}

    for job in jobs.get("jobs", []):
        gate = MAPPING.get(job.get("name"))
        if not gate:
            continue
        conclusion = job.get("conclusion")
        if conclusion == "success":
            gates[gate] = "PASS"
        elif conclusion == "skipped":
            gates[gate] = "SKIPPED"
        elif conclusion:
            gates[gate] = "FAIL"

    payload = {
        "sha": target_sha,
        "run_id": run_id,
        "status": (
            "PASS" if all(value in {"PASS", "SKIPPED"} for value in gates.values()) else "FAIL"
        ),
        "gates": gates,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    (EVIDENCE_DIR / f"{target_sha}.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def commit_timestamp(path: Path) -> int:
    git_executable = shutil.which("git")
    if not git_executable:
        return 0
    result = subprocess.run(  # nosec B603 - executable is resolved from PATH; arguments are fixed
        [git_executable, "show", "-s", "--format=%ct", path.stem],
        capture_output=True,
        text=True,
        check=False,
        cwd=ROOT,
    )
    return int(result.stdout.strip()) if result.returncode == 0 else 0


def prune() -> None:
    files = sorted(EVIDENCE_DIR.glob("*.json")) if EVIDENCE_DIR.exists() else []
    if len(files) <= 100:
        print(f"State evidence count: {len(files)}; nothing to prune.")
        return
    files.sort(key=lambda path: (commit_timestamp(path), path.name), reverse=True)
    for path in files[100:]:
        print(f"Removing old state evidence: {path}")
        path.unlink()
    print("State evidence retained: 100")


if __name__ == "__main__":
    command = os.environ.get("CI_STATE_COMMAND", "")
    if command == "collect":
        collect()
    elif command == "prune":
        prune()
    else:
        raise SystemExit("CI_STATE_COMMAND must be collect or prune")
