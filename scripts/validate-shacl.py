#!/usr/bin/env python3
"""
Validate every ontology TTL against the SHACL shapes declared in the register.
Specifically enforces the multilingual rule from core/shapes.shacl: every
SKOS concept must have prefLabel and definition in en, es, zh and ro.
"""

import sys
from pathlib import Path

from rdflib import Graph
from pyshacl import validate

REPO_ROOT  = Path(__file__).resolve().parent.parent
ONTO_DIR   = REPO_ROOT / "_sources" / "ontology"
SHAPES_PATH = ONTO_DIR / "core" / "shapes.shacl"


def main() -> int:
    if not SHAPES_PATH.exists():
        print(f"!! missing {SHAPES_PATH}", file=sys.stderr)
        return 1

    data_graph = Graph()
    for ttl in sorted(ONTO_DIR.rglob("*.ttl")):
        data_graph.parse(ttl, format="turtle")
    print(f"Loaded {len(data_graph)} triples from {sum(1 for _ in ONTO_DIR.rglob('*.ttl'))} TTL files.")

    shape_graph = Graph().parse(SHAPES_PATH, format="turtle")

    conforms, _, report = validate(
        data_graph,
        shacl_graph=shape_graph,
        inference="rdfs",
        meta_shacl=False,
        debug=False
    )

    if not conforms:
        print("SHACL VALIDATION FAILED:\n")
        print(report)
        return 1
    print("OK: all SKOS concepts have multilingual labels and definitions.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
