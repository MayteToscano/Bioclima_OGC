# BioClima OGC Building Blocks

**Status:** under development · **License:** CC-BY 4.0 · **Languages:** EN · ES · ZH · RO

A register of [OGC Building Blocks](https://ogcincubator.github.io/bblocks-docs/) for biodiversity and climate monitoring. The register models Essential Biodiversity Variables (EBVs), the indicators derived from them, the bioclimatic zonification those indicators produce, the provenance of every artefact, and the alignment with international policy frameworks — all anchored to a multilingual ontology.

The pilot dataset is the **Start of the Vegetation Active Period in Finland (2001-2018)** from the [GeoBON EBV portal](https://portal.geobon.org), modelled in CoverageJSON and shipped inside its building block.

---

## What is in this register

The register groups **18 building blocks** into five logical families. Every block lives under `_sources/`. Data files (CoverageJSON, GeoJSON) live inside the `examples/` folder of the block they belong to — there is no separate data directory.

```
Family E — Ontology      → defines what every term means in en/es/zh/ro
Family A — CoverageJSON  → constrains how spatiotemporal data is packaged
Family B — EBVs          → describes biodiversity observations (input data)
Family C — Indicators    → describes computed indices and zonifications
Family D — Provenance &
           Policy        → who produced each artefact, and what policy it serves
```

| # | Block | Family | What it does |
|---|---|---|---|
| 1 | `ontology.core` | E | Namespaces and concept schemes; declares the multilingual SHACL rule |
| 2 | `ontology.ebv-vocabulary` | E | SKOS terms for EBV classes, names and observed properties |
| 3 | `ontology.indicator-vocabulary` | E | SKOS terms for indicators and zonification categories |
| 4 | `ontology.units-and-measures` | E | Units of measurement (day of year, days/year, degree) |
| 5 | `ontology.entity-types` | E | Observed entities (coniferous forest, deciduous vegetation, etc.) |
| 6 | `ontology.policy-vocabulary` | E | KMGBF targets and SDG 15 concepts |
| 7 | `coveragejson.bioclima-coverage` | A | Profile of OGC CoverageJSON for BioClima |
| 8 | `ebv.ebv-definition` | B | Generic schema for any EBV record |
| 9 | `ebv.vegetation-phenology` | B | Thematic category covering phenology EBVs |
| 10 | `ebv.vap-coniferous` | B | **Real dataset:** VAP in Finnish coniferous forests, 2001-2018 |
| 11 | `ebv.vap-deciduous` | B | **Real dataset:** VAP in Finnish deciduous vegetation, 2001-2018 |
| 12 | `indicator.indicator-definition` | C | Generic schema for any indicator (recipe-style) |
| 13 | `indicator.pci` | C | Phenological Change Indicator + Python implementation |
| 14 | `indicator.bioclimatic-zone` | C | Zonification from PCI + Python implementation |
| 15 | `provenance.ebv-provenance` | D | PROV-O for EBV datasets |
| 16 | `provenance.indicator-provenance` | D | PROV-O for indicators (with git commit hash) |
| 17 | `policy.kmgbf-target` | D | Schema for Kunming-Montreal GBF targets |
| 18 | `policy.policy-alignment` | D | Indicator ↔ policy relationships |

---

## Why this register exists

Environmental monitoring suffers three chronic problems that this register tackles head-on:

**Disconnection between climate and biodiversity data.** Climate data and biodiversity data are usually monitored in silos. This register models both EBV observations (what we see in the ecosystem) and the indicators that turn them into actionable signals, with a common provenance and policy layer on top.

**Lack of standardisation for EBVs.** OGC building blocks already exist for generic geospatial data, but not for biodiversity-specific structures (EBV class hierarchy, MODIS-derived phenology metrics, multilingual scientific definitions). This register fills that gap by extending CoverageJSON and adding seven BioClima-specific blocks.

**Weak link to decision-making.** Numerical indicators rarely carry an explicit semantic bridge to international commitments. Every indicator in this register declares its alignment with Kunming-Montreal GBF targets and SDG 15, with multilingual justifications and an evidence-strength tag.

---

## Audience

The register is intended for several communities at once:

**Developers and standards implementers** can reuse the CoverageJSON profile, the EBV schemas and the SHACL shapes to build interoperable monitoring platforms.

**Data providers** (research institutes, environmental agencies, GeoBON contributors) can publish their EBV datasets following the `ebv.ebv-definition` template, inheriting metadata, provenance and policy alignment for free.

**Domain scientists** can extend the indicator family with new computations — the `recipe.jsonld` + `compute.py` pattern accepts any Python code and the GitHub Actions take care of re-running it.

**Policy-makers** can read the indicator outputs in the viewer, click any cell or zone, and see directly which KMGBF target it informs and how strong the evidence is.

---

## How to use this register

### As a reader

Open the **viewer** at `viewer/index.html` (or the GitHub Pages URL once deployed). You can switch languages, pick any of the registered layers (the two EBVs, the computed PCI, the bioclimatic zones), play the temporal animation for time-varying datasets, and click on the map to see the value at that location together with its multilingual definition and policy relevance.

### As a contributor

Adding a new EBV is a single-step operation:

1. Create a folder under `_sources/ebv/<your-ebv-id>/`.
2. Add a `bblock.json` declaring `dependsOn` of `ogc.bioclima.ebv.ebv-definition` and `ogc.bioclima.coveragejson.bioclima-coverage`.
3. Add a `metadata.jsonld` filled in like the existing `vap-coniferous` example.
4. Drop your CoverageJSON file inside the block's `examples/` folder.
5. Append an entry to `viewer/data/layers.json` so the viewer picks it up automatically.

Adding a new indicator follows the same pattern but with a `code/` folder containing a Python implementation and a `recipe.jsonld` declaring the inputs and parameters. The CI will automatically re-run the indicator whenever any input EBV changes.

If your new dataset introduces unseen vocabulary terms (a new observed property, a new entity type), extend the relevant ontology TTL file and re-run `python scripts/build-concepts-index.py` to refresh the viewer's lookup index.

### As a CI operator

Two GitHub Actions live under `github/workflows/` (the directory is deliberately named without the leading dot to avoid the rendering bug some toolchains have with hidden folders; the deployment workflow renames it to `.github/workflows/` if your runner needs it — see the note below).

- `bblocks-validate.yml` runs on every push and PR. It validates every `bblock.json`, parses every `schema.yaml`, runs the SHACL multilingual rule against all ontologies, builds `viewer/data/concepts.json`, and assembles `build/register.json`.
- `recompute-indicators.yml` runs when an EBV file or any indicator code changes. It recomputes PCI, regenerates the zonification, stamps the provenance file with the current git commit, and commits the new outputs back to the repository.

> **About the workflow directory:** GitHub Actions only honours the canonical `.github/workflows/` path. If you keep the directory as `github/workflows/` (without the dot), the CI will not trigger. Two options: rename the folder to `.github/workflows/` after pushing, or keep `github/workflows/` for editing convenience and add a symlink/CI step that copies the files into the canonical location.

---

## How indicators are computed

The link between semantic description and actual computation is intentionally explicit. Every indicator has:

- A **`recipe.jsonld`** that declares, in machine-readable form: the inputs (which EBV bblocks), the parameters (e.g. coniferous weight 0.4, deciduous weight 0.6, OLS trend method), the output unit (days per year), and a pointer to the implementation entry point (`compute.py#compute_pci`).
- A **`code/compute.py`** that implements the recipe in plain Python. It can be re-run from the command line locally or by the GitHub Action automatically.
- A **`code/requirements.txt`** so anyone can reproduce the environment.

The PCI fits a per-pixel ordinary-least-squares trend to the VAP day-of-year time series for coniferous and deciduous forests, then takes their weighted mean. The bioclimatic zonification classifies each PCI cell into one of four categories (stable, mild advance, strong advance, delay), each enriched with its SKOS IRI and the KMGBF targets it informs. Running the pipeline on the Finnish data produces about 13,600 valid PCI pixels with trends ranging from −0.77 to +0.81 days/year.

---

## Provenance and quality

Every published artefact carries a PROV-O record. For an EBV, this includes the raw satellite source (MODIS Terra L1B), the processing agent (SYKE/VTT), and the methodology citation. For an indicator, the record additionally captures the exact git commit hash of the implementation, the GitHub Actions run ID, and the numerical parameters used. This makes any indicator value reproducible from raw inputs to final number.

---

## Repository layout

```
Bioclima_OGC/
├── _sources/                        ← all building blocks live here
│   ├── ontology/                    ← 6 ontology blocks (en/es/zh/ro SKOS)
│   ├── coveragejson/                ← BioClima CoverageJSON profile
│   ├── ebv/                         ← EBV schemas + concrete datasets
│   ├── indicator/                   ← PCI and bioclimatic-zone (with code/)
│   ├── provenance/                  ← PROV-O for EBVs and indicators
│   └── policy/                      ← KMGBF targets and policy alignment
├── viewer/                          ← generic Leaflet viewer
│   ├── index.html
│   ├── css/viewer.css
│   ├── js/  (i18n.js, covjson.js, viewer.js)
│   └── data/  (layers.json, concepts.json)
├── github/workflows/                ← CI (validate + recompute)
├── scripts/                         ← register builder, validators, prov stamper
├── docs/                            ← generated documentation (CI output)
├── bblocks-config.yaml              ← register configuration
├── LICENSE
└── README.md
```

---

## Standards and references

- [OGC CoverageJSON Community Standard 21-069r2](https://docs.ogc.org/cs/21-069r2/21-069r2.html)
- [OGC Building Blocks documentation](https://ogcincubator.github.io/bblocks-docs/)
- [W3C SKOS Reference](https://www.w3.org/TR/skos-reference/)
- [W3C PROV-O](https://www.w3.org/TR/prov-o/)
- [W3C SHACL](https://www.w3.org/TR/shacl/)
- [GeoBON EBV portal](https://portal.geobon.org)
- [Kunming-Montreal Global Biodiversity Framework](https://www.cbd.int/doc/decisions/cop-15/cop-15-dec-04-en.pdf)
- Böttcher, K. et al. (2014). [MODIS-derived VAP in Finland](https://doi.org/10.1016/j.rse.2013.09.022). *RSE*.
- Böttcher, K. et al. (2016). [Phenology in deciduous vegetation from NDWI](https://doi.org/10.3390/rs8070580). *Remote Sensing*.

---

## License and citation

Data and content are released under [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/). Code is released under [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0). If you use this register, please cite the GeoBON DOI `10.25829/xf8ek6` for the underlying data and the BioClima project for the register itself.
