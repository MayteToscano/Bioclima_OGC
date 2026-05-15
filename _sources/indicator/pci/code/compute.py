"""
Phenological Change Indicator (PCI)
===================================
Implementation referenced by recipe.jsonld of
ogc.bioclima.indicator.pci.

Reads two BioClima CoverageJSON cubes (coniferous and deciduous VAP-DOY),
fits a per-pixel ordinary-least-squares trend over the time axis, combines
them with the published weights and writes a new CoverageJSON cube with
trend values in days/year.

Run as a script:
    python compute.py \\
        --coniferous ../../ebv/vap-coniferous/examples/finland-vap-coniferous-2001-2018.covjson \\
        --deciduous  ../../ebv/vap-deciduous/examples/finland-vap-deciduous-2001-2018.covjson \\
        --output     examples/pci-finland-2001-2018.covjson
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Tuple

import numpy as np

# Default parameters (kept in sync with recipe.jsonld)
DEFAULT_CONIF_WEIGHT  = 0.4
DEFAULT_DECID_WEIGHT  = 0.6
DEFAULT_NODATA        = -32768
DEFAULT_MIN_YEARS     = 8


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_cube(path: Path, param_name: str = "vap_doy"):
    """Load a CoverageJSON cube and return (data_array[t,y,x], years, axes, nodata).

    Raises ValueError if the structure is not a 3-D NdArray with axes (t, y, x).
    """
    with path.open() as fh:
        cov = json.load(fh)

    rng = cov["ranges"][param_name]
    if rng["axisNames"] != ["t", "y", "x"]:
        raise ValueError(f"Expected axes (t, y, x), got {rng['axisNames']}")

    shape  = tuple(rng["shape"])           # (t, y, x)
    nodata = rng.get("nodata", DEFAULT_NODATA)
    data   = np.asarray(rng["values"], dtype=np.float32).reshape(shape)
    data[data == nodata] = np.nan

    years = [int(v[:4]) for v in cov["domain"]["axes"]["t"]["values"]]
    return data, np.asarray(years, dtype=np.float32), cov["domain"], nodata


# ---------------------------------------------------------------------------
# Core computation
# ---------------------------------------------------------------------------

def per_pixel_trend(cube: np.ndarray, years: np.ndarray,
                    min_years: int = DEFAULT_MIN_YEARS) -> np.ndarray:
    """Ordinary least-squares slope (days/year) over the time axis of `cube`.

    Pixels with fewer than `min_years` valid observations are returned as NaN.
    Vectorised closed-form solution; no Python loop over pixels.
    """
    T = cube.shape[0]
    if years.shape[0] != T:
        raise ValueError("years length does not match cube time axis")

    # Mask of valid observations
    valid = ~np.isnan(cube)                          # (T, Y, X)
    n     = valid.sum(axis=0)                        # (Y, X)

    # Replace NaNs with 0 for the sum, but keep them out via `valid`
    cube_z = np.where(valid, cube, 0.0)
    x      = years.reshape(T, 1, 1)
    x_z    = np.where(valid, x, 0.0)

    sum_x  = x_z.sum(axis=0)
    sum_y  = cube_z.sum(axis=0)
    sum_xy = (x_z * cube_z).sum(axis=0)
    sum_xx = (x_z * x_z).sum(axis=0)

    denom = n * sum_xx - sum_x * sum_x
    with np.errstate(invalid="ignore", divide="ignore"):
        slope = (n * sum_xy - sum_x * sum_y) / denom
    slope[n < min_years] = np.nan
    slope[denom == 0]    = np.nan
    return slope


def combine(coniferous: np.ndarray, deciduous: np.ndarray,
            w_conif: float = DEFAULT_CONIF_WEIGHT,
            w_decid: float = DEFAULT_DECID_WEIGHT) -> np.ndarray:
    """Weighted mean of the two slope grids, robust to NaNs.

    If both inputs are NaN the result is NaN; if only one is present the
    available value is used (its weight becomes 1).
    """
    cw = np.where(np.isnan(coniferous), 0.0, w_conif)
    dw = np.where(np.isnan(deciduous),  0.0, w_decid)
    total = cw + dw

    cz = np.where(np.isnan(coniferous), 0.0, coniferous)
    dz = np.where(np.isnan(deciduous),  0.0, deciduous)

    with np.errstate(invalid="ignore", divide="ignore"):
        out = (cz * cw + dz * dw) / total
    out[total == 0] = np.nan
    return out


# ---------------------------------------------------------------------------
# Output writer
# ---------------------------------------------------------------------------

def build_pci_coverage(pci: np.ndarray, source_domain: dict,
                       year_start: int, year_end: int) -> dict:
    """Wrap the PCI grid in a BioClima CoverageJSON document."""
    nodata = -9999.0
    flat = np.where(np.isnan(pci), nodata, pci).astype(np.float32).ravel().tolist()

    return {
        "type": "Coverage",
        "domain": {
            "type": "Domain",
            "domainType": "Grid",
            "axes": {
                "x": source_domain["axes"]["x"],
                "y": source_domain["axes"]["y"]
            },
            "referencing": [r for r in source_domain["referencing"]
                            if "t" not in r["coordinates"]]
        },
        "parameters": {
            "pci": {
                "type": "Parameter",
                "observedProperty": {
                    "id": "https://maytetoscano.github.io/Bioclima_OGC/def/indicator/pci",
                    "label": {
                        "en": "Phenological Change Indicator",
                        "es": "Indicador de cambio fenológico",
                        "zh": "物候变化指标",
                        "ro": "Indicator al schimbării fenologice"
                    }
                },
                "unit": {
                    "id": "https://maytetoscano.github.io/Bioclima_OGC/def/units/days-per-year",
                    "symbol": "d/yr"
                }
            }
        },
        "ranges": {
            "pci": {
                "type": "NdArray",
                "dataType": "float",
                "axisNames": ["y", "x"],
                "shape": list(pci.shape),
                "nodata": nodata,
                "values": flat
            }
        },
        "metadata": {
            "title": {
                "en": f"PCI for Finland, {year_start}-{year_end}",
                "es": f"PCI para Finlandia, {year_start}-{year_end}",
                "zh": f"芬兰 PCI,{year_start}-{year_end}",
                "ro": f"PCI pentru Finlanda, {year_start}-{year_end}"
            },
            "computed_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
            "computed_from": [
                "ogc.bioclima.ebv.vap-coniferous",
                "ogc.bioclima.ebv.vap-deciduous"
            ],
            "recipe": "https://maytetoscano.github.io/Bioclima_OGC/bblock/ogc.bioclima.indicator.pci/recipe.jsonld"
        }
    }


# ---------------------------------------------------------------------------
# Public API (referenced from recipe.jsonld#implementation.entrypoint)
# ---------------------------------------------------------------------------

def compute_pci(coniferous_path: str, deciduous_path: str,
                coniferous_weight: float = DEFAULT_CONIF_WEIGHT,
                deciduous_weight: float = DEFAULT_DECID_WEIGHT) -> dict:
    """End-to-end PCI computation; returns a CoverageJSON dict."""
    conif, c_years, c_dom, _ = load_cube(Path(coniferous_path))
    decid, d_years, _,    _  = load_cube(Path(deciduous_path))

    if conif.shape[1:] != decid.shape[1:]:
        raise ValueError(f"Grid shapes differ: {conif.shape[1:]} vs {decid.shape[1:]}")

    slope_c = per_pixel_trend(conif, c_years)
    slope_d = per_pixel_trend(decid, d_years)
    pci     = combine(slope_c, slope_d, coniferous_weight, deciduous_weight)

    return build_pci_coverage(pci, c_dom,
                              int(min(c_years.min(), d_years.min())),
                              int(max(c_years.max(), d_years.max())))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cli() -> None:
    p = argparse.ArgumentParser(description="Compute the PCI from two VAP cubes.")
    p.add_argument("--coniferous", required=True, type=Path)
    p.add_argument("--deciduous",  required=True, type=Path)
    p.add_argument("--output",     required=True, type=Path)
    p.add_argument("--w-coniferous", type=float, default=DEFAULT_CONIF_WEIGHT)
    p.add_argument("--w-deciduous",  type=float, default=DEFAULT_DECID_WEIGHT)
    args = p.parse_args()

    cov = compute_pci(str(args.coniferous), str(args.deciduous),
                      args.w_coniferous, args.w_deciduous)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w") as fh:
        json.dump(cov, fh)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    _cli()
