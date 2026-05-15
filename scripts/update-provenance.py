#!/usr/bin/env python3
"""
Stamp the indicator-provenance example with the current git commit hash and
the GitHub Actions run id so that the on-disk provenance reflects the actual
run that produced the indicator outputs.
"""

import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PROV_PATH = REPO_ROOT / "_sources" / "provenance" / "indicator-provenance" / "examples" / "pci-provenance.jsonld"


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
        ).strip()
    except subprocess.CalledProcessError:
        return "unknown"


def main() -> int:
    data = json.loads(PROV_PATH.read_text(encoding="utf-8"))
    now  = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

    data["wasGeneratedBy"]["scriptVersion"] = git_sha()
    data["wasGeneratedBy"]["runId"]        = os.environ.get("GITHUB_RUN_ID", "local")
    data["wasGeneratedBy"]["endedAtTime"]  = now
    if "startedAtTime" not in data["wasGeneratedBy"]:
        data["wasGeneratedBy"]["startedAtTime"] = now

    PROV_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Stamped {PROV_PATH} with commit {data['wasGeneratedBy']['scriptVersion'][:8]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
