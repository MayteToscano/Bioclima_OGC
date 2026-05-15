#!/usr/bin/env python3
"""
Assemble build/register.json from every bblock.json in the register.
This emulates what the upstream `bblocks-postprocess` tool would do, in a
self-contained way that does not require Docker.
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCES   = REPO_ROOT / "_sources"
OUTPUT    = REPO_ROOT / "build" / "register.json"


def main() -> int:
    bblocks = []
    for manifest in sorted(SOURCES.rglob("bblock.json")):
        data = json.loads(manifest.read_text(encoding="utf-8"))
        data["_path"] = str(manifest.relative_to(REPO_ROOT))
        bblocks.append(data)

    register = {
        "register": "bioclima",
        "title": "BioClima OGC Building Blocks",
        "description": "OGC Building Blocks for Essential Biodiversity Variables, indicators, provenance and policy alignment, with multilingual SKOS ontology (en/es/zh/ro).",
        "bblocks": bblocks,
        "count": len(bblocks)
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(register, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {OUTPUT}: {len(bblocks)} building blocks.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
