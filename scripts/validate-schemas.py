#!/usr/bin/env python3
"""Validate every bblock.json has the required fields and every schema.yaml is parseable."""

import sys
import json
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCES   = REPO_ROOT / "_sources"

REQUIRED_BBLOCK_FIELDS = ["itemIdentifier", "name", "abstract", "itemClass", "version"]

def main() -> int:
    errors = []
    n_bblocks = 0

    for manifest in SOURCES.rglob("bblock.json"):
        n_bblocks += 1
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            errors.append(f"{manifest}: invalid JSON ({e})")
            continue
        for field in REQUIRED_BBLOCK_FIELDS:
            if field not in data:
                errors.append(f"{manifest}: missing field '{field}'")

    for schema in SOURCES.rglob("schema.yaml"):
        try:
            yaml.safe_load(schema.read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            errors.append(f"{schema}: invalid YAML ({e})")

    if errors:
        print("Validation FAILED:")
        for e in errors:
            print("  -", e)
        return 1
    print(f"OK: {n_bblocks} bblock.json files validated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
