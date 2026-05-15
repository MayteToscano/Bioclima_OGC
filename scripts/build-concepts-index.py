#!/usr/bin/env python3
"""
Build viewer/data/concepts.json - a flat JSON mirror of every SKOS concept
in the BioClima ontology so the static viewer can resolve IRIs without a
Turtle parser. Uses rdflib for reliable Turtle parsing.

Invoked by the bblocks-validate GitHub Action and by the local dev workflow.
"""

from __future__ import annotations
import json
import sys
from pathlib import Path

from rdflib import Graph
from rdflib.namespace import SKOS, RDF

REPO_ROOT = Path(__file__).resolve().parent.parent
ONTO_DIR  = REPO_ROOT / "_sources" / "ontology"
OUT_PATH  = REPO_ROOT / "viewer" / "data" / "concepts.json"


def main() -> int:
    g = Graph()
    n_files = 0
    for ttl in sorted(ONTO_DIR.rglob("*.ttl")):
        try:
            g.parse(ttl, format="turtle")
            n_files += 1
            print(f"  parsed {ttl.relative_to(REPO_ROOT)}")
        except Exception as e:
            print(f"!! failed {ttl}: {e}", file=sys.stderr)
            return 1

    index = {}
    for concept in g.subjects(RDF.type, SKOS.Concept):
        iri = str(concept)
        labels = {str(o.language or "und"): str(o) for o in g.objects(concept, SKOS.prefLabel)}
        defs   = {str(o.language or "und"): str(o) for o in g.objects(concept, SKOS.definition)}
        index[iri] = {"label": labels, "definition": defs}

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote {OUT_PATH}")
    print(f"  {len(index)} concepts from {n_files} TTL files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
