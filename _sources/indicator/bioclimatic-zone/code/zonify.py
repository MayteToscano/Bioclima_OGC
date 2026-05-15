"""
Bioclimatic zonification from the PCI CoverageJSON.
===================================================
Implementation referenced by recipe.jsonld of
ogc.bioclima.indicator.bioclimatic-zone.

Light-weight implementation that avoids heavy GIS dependencies: we classify
every PCI cell into one of four categories with simple numpy thresholds, then
emit a GeoJSON FeatureCollection where each feature is a single grid cell
polygon enriched with its statistics, the SKOS IRI of its category and the
KMGBF target it informs. The viewer can render these features directly.

A production version could replace the per-cell polygon by a true contiguity
algorithm (rasterio.features.shapes) once those dependencies become available.
"""

from __future__ import annotations
import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Tuple

import numpy as np


# Thresholds mirror recipe.jsonld
THRESHOLDS = [
    ("strong_advance", -1e9, -0.5),
    ("mild_advance",   -0.5, -0.2),
    ("stable",         -0.2,  0.2),
    ("delay",           0.2,  1e9),
]

CATEGORY_IRIS = {
    "stable":         "https://maytetoscano.github.io/Bioclima_OGC/def/indicator/zone-stable",
    "mild_advance":   "https://maytetoscano.github.io/Bioclima_OGC/def/indicator/zone-mild-advance",
    "strong_advance": "https://maytetoscano.github.io/Bioclima_OGC/def/indicator/zone-strong-advance",
    "delay":          "https://maytetoscano.github.io/Bioclima_OGC/def/indicator/zone-delay",
}

CATEGORY_LABELS = {
    "stable": {
        "en": "Stable phenology zone",
        "es": "Zona de fenología estable",
        "zh": "物候稳定区",
        "ro": "Zonă cu fenologie stabilă"
    },
    "mild_advance": {
        "en": "Mild phenological advance",
        "es": "Adelanto fenológico leve",
        "zh": "物候轻微提前",
        "ro": "Avans fenologic ușor"
    },
    "strong_advance": {
        "en": "Strong phenological advance",
        "es": "Adelanto fenológico fuerte",
        "zh": "物候强烈提前",
        "ro": "Avans fenologic puternic"
    },
    "delay": {
        "en": "Phenological delay zone",
        "es": "Zona de retraso fenológico",
        "zh": "物候延迟区",
        "ro": "Zonă cu întârziere fenologică"
    },
}


def classify(pci_array: np.ndarray) -> np.ndarray:
    """Map continuous PCI values to category strings; NaN -> None."""
    out = np.full(pci_array.shape, None, dtype=object)
    for cat, lo, hi in THRESHOLDS:
        mask = (~np.isnan(pci_array)) & (pci_array >= lo) & (pci_array < hi)
        out[mask] = cat
    return out


def cell_polygon(lon: float, lat: float, dx: float, dy: float):
    """Return a GeoJSON polygon for a single cell centered at (lon, lat)."""
    hx, hy = dx / 2.0, dy / 2.0
    return [[[lon - hx, lat - hy],
             [lon + hx, lat - hy],
             [lon + hx, lat + hy],
             [lon - hx, lat + hy],
             [lon - hx, lat - hy]]]


def zonify(pci_covjson_path: str, downsample: int = 4) -> dict:
    """Read the PCI CoverageJSON and return a GeoJSON FeatureCollection.

    `downsample` keeps the example output manageable: only every n-th cell
    is emitted. Set to 1 to keep all valid pixels.
    """
    with open(pci_covjson_path) as fh:
        cov = json.load(fh)

    rng    = cov["ranges"]["pci"]
    shape  = tuple(rng["shape"])           # (y, x)
    nodata = rng.get("nodata", -9999)
    data   = np.asarray(rng["values"], dtype=np.float32).reshape(shape)
    data[data == nodata] = np.nan

    def axis_values(ax):
        if "values" in ax and ax["values"]:
            return np.asarray(ax["values"], dtype=np.float64)
        return np.linspace(ax["start"], ax["stop"], ax["num"], dtype=np.float64)

    xs = axis_values(cov["domain"]["axes"]["x"])
    ys = axis_values(cov["domain"]["axes"]["y"])

    if len(xs) < 2 or len(ys) < 2:
        raise ValueError("Cannot compute cell size from coverage axes")
    dx = float(abs(xs[1] - xs[0]))
    dy = float(abs(ys[1] - ys[0]))

    labels = classify(data)

    features = []
    fid = 0
    for j in range(0, shape[0], downsample):
        for i in range(0, shape[1], downsample):
            cat = labels[j, i]
            if cat is None:
                continue
            features.append({
                "type": "Feature",
                "id": f"zone-{fid:05d}",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": cell_polygon(float(xs[i]), float(ys[j]), dx, dy)
                },
                "properties": {
                    "category": CATEGORY_IRIS[cat],
                    "categoryKey": cat,
                    "categoryLabel": CATEGORY_LABELS[cat],
                    "pci_value": float(data[j, i]),
                    "policyRelevance": [
                        "https://maytetoscano.github.io/Bioclima_OGC/def/policy/kmgbf-target-1",
                        "https://maytetoscano.github.io/Bioclima_OGC/def/policy/kmgbf-target-8"
                    ]
                }
            })
            fid += 1

    return {
        "type": "FeatureCollection",
        "name": "BioClima bioclimatic zones (Finland, PCI-based)",
        "metadata": {
            "computed_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
            "derivedFrom": "ogc.bioclima.indicator.pci",
            "downsample": downsample,
            "thresholds": {c: {"min": lo, "max": hi} for c, lo, hi in THRESHOLDS}
        },
        "features": features
    }


def _cli() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--pci",        required=True, type=Path)
    p.add_argument("--output",     required=True, type=Path)
    p.add_argument("--downsample", type=int, default=4)
    args = p.parse_args()

    fc = zonify(str(args.pci), downsample=args.downsample)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w") as fh:
        json.dump(fc, fh)
    print(f"Wrote {args.output} ({len(fc['features'])} features)")


if __name__ == "__main__":
    _cli()
