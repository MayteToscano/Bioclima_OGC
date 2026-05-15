#!/usr/bin/env python3
"""
Local lint that emulates the key validations bblocks-postprocess performs.
Designed to catch the kinds of errors that were appearing in CI before:

  - missing 'dateTimeAddition'        (NOT dateTimeAddedToRegister)
  - duplicate 'schema' field          (schema.yaml is auto-detected)
  - dependsOn referencing missing IDs (the recurring 7/8/9 errors)
  - non-existent itemClass enum

Run as: python scripts/lint-bblocks.py
"""

from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC  = ROOT / "_sources"

REQUIRED_FIELDS = ["itemIdentifier", "name", "abstract", "status",
                   "dateTimeAddition", "itemClass", "version"]
ALLOWED_ITEM_CLASSES = {"schema", "api", "datatype", "parameter",
                        "path", "header", "query-parameter",
                        "cookie", "response", "ontology"}


def main() -> int:
    errors = []
    block_ids = set()
    manifests = []

    for f in sorted(SRC.rglob("bblock.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            errors.append(f"{f}: invalid JSON: {e}")
            continue
        manifests.append((f, data))
        block_ids.add(data.get("itemIdentifier"))

    print(f"Found {len(manifests)} bblock.json files\n")

    for path, data in manifests:
        rel = path.relative_to(ROOT)

        # 1. required fields
        for field in REQUIRED_FIELDS:
            if field not in data:
                errors.append(f"{rel}: missing required field '{field}'")

        # 2. legacy field that triggered earlier failures
        if "dateTimeAddedToRegister" in data:
            errors.append(f"{rel}: uses legacy 'dateTimeAddedToRegister' — should be 'dateTimeAddition'")

        # 3. schema autodetection: do NOT declare 'schema' if schema.yaml exists
        schema_yaml = path.parent / "schema.yaml"
        if schema_yaml.exists() and "schema" in data:
            errors.append(f"{rel}: redundant 'schema' field (schema.yaml is auto-detected)")

        # 4. itemClass must be valid
        ic = data.get("itemClass")
        if ic is not None and ic not in ALLOWED_ITEM_CLASSES:
            errors.append(f"{rel}: itemClass '{ic}' not in {sorted(ALLOWED_ITEM_CLASSES)}")

        # 5. dependsOn must reference existing blocks (or external imports)
        for dep in data.get("dependsOn", []):
            if dep.startswith("ogc.bioclima.") and dep not in block_ids:
                errors.append(f"{rel}: dependsOn '{dep}' does not exist in _sources/")

        # 6. examples.yaml must exist if examples/ directory present
        ex_dir = path.parent / "examples"
        ex_yaml = path.parent / "examples.yaml"
        if ex_dir.exists() and not ex_yaml.exists():
            errors.append(f"{rel}: has examples/ directory but no examples.yaml")

    if errors:
        print("LINT FAILED:")
        for e in errors:
            print("  ✗", e)
        return 1

    print(f"OK — all {len(manifests)} blocks pass the lint checks.")
    print("Block ids:")
    for b in sorted(block_ids):
        print(f"  • {b}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
