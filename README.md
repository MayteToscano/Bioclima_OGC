# BioClima OGC Building Blocks

**Status:** under development · **License:** CC-BY 4.0 · **Languages:** EN · ES · ZH · RO

A register of [OGC Building Blocks](https://ogcincubator.github.io/bblocks-docs/) for biodiversity and climate monitoring. The register models Essential Biodiversity Variables (EBVs), the indicators derived from them, the bioclimatic zonification those indicators produce, the provenance of every artefact, and the alignment with international policy frameworks — all anchored to a multilingual ontology.

The pilot dataset is the **Start of the Vegetation Active Period in Finland (2001-2018)** from the [GeoBON EBV portal](https://portal.geobon.org), modelled in CoverageJSON and shipped inside its building block.

---

## What is in this register

The register defines **11 building blocks** under `_sources/`. Data files (CoverageJSON, GeoJSON) live inside the `examples/` folder of the block they belong to — there is no separate data directory. The multilingual SKOS ontology lives outside `_sources/` (at `ontology/`) and is referenced by IRI from the blocks.

```
Family A — CoverageJSON profile     (1 block)  packaging of spatiotemporal data
Family B — EBV schemas + datasets   (3 blocks) generic template + 2 real datasets
Family C — Indicators               (3 blocks) generic + PCI + zonification (with Python)
Family D — Provenance + Policy      (4 blocks) PROV-O + KMGBF targets + alignment
                                    ──────────
                                    11 blocks
```

| Block | Family | What it does |
|---|---|---|
| `ogc.bioclima.coveragejson.bioclima-coverage` | A | Profile of OGC CoverageJSON for BioClima (EPSG:4326, multilingual labels) |
| `ogc.bioclima.ebv.ebv-definition` | B | Generic GeoBON-style schema for any EBV record |
| `ogc.bioclima.ebv.vap-coniferous` | B | Real dataset: VAP in Finnish coniferous forests, 2001-2018 |
| `ogc.bioclima.ebv.vap-deciduous` | B | Real dataset: VAP in Finnish deciduous vegetation, 2001-2018 |
| `ogc.bioclima.indicator.indicator-definition` | C | Generic recipe-style schema for any indicator |
| `ogc.bioclima.indicator.pci` | C | Phenological Change Indicator + Python implementation |
| `ogc.bioclima.indicator.bioclimatic-zone` | C | Zonification from PCI + Python implementation |
| `ogc.bioclima.provenance.ebv-provenance` | D | PROV-O record for EBVs |
| `ogc.bioclima.provenance.indicator-provenance` | D | PROV-O record for indicators (with git commit hash) |
| `ogc.bioclima.policy.kmgbf-target` | D | Schema for Kunming-Montreal GBF targets |
| `ogc.bioclima.policy.policy-alignment` | D | Indicator ↔ KMGBF target relationships |

---

## Why this register exists

Environmental monitoring suffers three chronic problems that this register tackles:

**Disconnection between climate and biodiversity data.** Climate data and biodiversity data are usually monitored in silos. This register models both EBV observations (what we see in the ecosystem) and the indicators that turn them into actionable signals, with a common provenance and policy layer on top.

**Lack of standardisation for EBVs.** OGC building blocks already exist for generic geospatial data, but not for biodiversity-specific structures (EBV class hierarchy, MODIS-derived phenology metrics, multilingual scientific definitions). This register fills that gap.

**Weak link to decision-making.** Numerical indicators rarely carry an explicit semantic bridge to international commitments. Every indicator here declares its alignment with Kunming-Montreal GBF targets and SDG 15, with multilingual justifications and an evidence-strength tag.

---

## Audience

**Developers and standards implementers** can reuse the CoverageJSON profile, the EBV schemas and the SHACL shapes.

**Data providers** can publish their EBV datasets following the `ebv.ebv-definition` template, inheriting metadata, provenance and policy alignment.

**Domain scientists** can extend the indicator family with new computations using the `recipe.jsonld` + `compute.py` pattern.

**Policy-makers** can read the indicator outputs in the viewer, click any cell or zone, and see which KMGBF target it informs.

---

## How to use this register

### As a reader

Open the viewer at `viewer/index.html` (or the GitHub Pages URL once deployed). Switch languages, pick layers (EBVs, PCI, bioclimatic zones), play the temporal animation, click on the map to see values together with multilingual definitions and policy relevance.

### As a contributor

Adding a new EBV:

1. Create `_sources/ebv/<your-ebv-id>/` with `bblock.json`, `description.md`, `examples.yaml` and `schema.yaml`.
2. Declare `dependsOn` of `ogc.bioclima.ebv.ebv-definition` and `ogc.bioclima.coveragejson.bioclima-coverage`.
3. Drop the CoverageJSON and `metadata.jsonld` inside the block's `examples/` folder.
4. Append an entry to `viewer/data/layers.json` so the viewer picks it up.

Adding a new ontology term: edit `ontology/bioclima-ontology.ttl` directly, adding `prefLabel` and `definition` in **all four languages**. The SHACL rule will reject anything missing a language.

### As a CI operator

Two GitHub Actions live under **`.github/workflows/`** (the canonical GitHub path with the leading dot, which is what GitHub honours):

- **`bblocks.yml`** runs on every push and PR. It first runs `scripts/lint-bblocks.py` (a local lint that mimics the OGC postprocess validations), then the official `ghcr.io/opengeospatial/bblocks-postprocess` Docker image, then SHACL validation of the ontology, then deploys everything to GitHub Pages.
- **`recompute-indicators.yml`** runs when an EBV file or any indicator code changes. It recomputes PCI, regenerates the zonification, stamps the provenance with the current git commit, and commits the new outputs back.

---

## Validation: what the lint catches before CI

The local lint (`python scripts/lint-bblocks.py`) catches the kinds of errors that previously broke the build:

| Error | What the lint detects |
|---|---|
| Missing `dateTimeAddition` | Required field absent |
| Legacy `dateTimeAddedToRegister` | Field renamed by OGC — the lint flags the old name |
| Duplicated `schema` declaration | Field present even though `schema.yaml` exists (it is auto-detected) |
| Broken `dependsOn` | A dependency references a block id that has no `bblock.json` in `_sources/` |
| Invalid `itemClass` | Value not in the OGC-allowed enum |
| Missing `examples.yaml` | Block has `examples/` directory but no manifest |

Pass the lint locally before committing and the CI will not fail on these.

---

## How indicators are computed

Every indicator has three artefacts that work together:

- **`recipe.jsonld`** declares semantically what the indicator computes (inputs, parameters, output unit, entry point).
- **`code/compute.py`** implements the recipe in plain Python.
- **`code/requirements.txt`** pins the dependencies.

The PCI fits a per-pixel ordinary-least-squares trend to the VAP day-of-year time series for coniferous and deciduous forests, then takes their weighted mean (0.4 coniferous, 0.6 deciduous). The bioclimatic zonification classifies each PCI cell into one of four categories using published thresholds.

Running the pipeline on the Finnish data produces about 13,600 valid PCI pixels with trends ranging from −0.77 to +0.81 days/year, and 857 categorised zone polygons.

---

## Provenance

Every published artefact carries a PROV-O record. For an EBV, this includes the raw satellite source (MODIS Terra L1B), the processing agent (SYKE/VTT), and the methodology citation. For an indicator, the record additionally captures the exact git commit hash of the implementation, the GitHub Actions run id, and the numerical parameters used.

---

## Repository layout

```
Bioclima_OGC/
├── _sources/                        all building blocks
│   ├── coveragejson/                A: CoverageJSON profile
│   ├── ebv/                         B: EBV template + 2 real datasets
│   ├── indicator/                   C: PCI + zonification (with code/)
│   ├── provenance/                  D1: PROV-O schemas
│   └── policy/                      D2: KMGBF + alignment
├── ontology/                        SKOS vocabulary (en/es/zh/ro) + SHACL
├── viewer/                          Leaflet viewer
│   ├── index.html
│   ├── css/viewer.css
│   ├── js/  (i18n.js, covjson.js, viewer.js)
│   └── data/ (layers.json, concepts.json — built by CI)
├── .github/workflows/               CI: validate + deploy + recompute
├── scripts/                         lint, SHACL check, concepts builder
├── bblocks-config.yaml              register configuration
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
- Böttcher, K. et al. (2014). [MODIS-derived VAP in Finland](https://doi.org/10.1016/j.rse.2013.09.022). *Remote Sensing of Environment*.
- Böttcher, K. et al. (2016). [Phenology in deciduous vegetation from NDWI](https://doi.org/10.3390/rs8070580). *Remote Sensing*.

---

## License and citation

Data and content are released under [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/). Code is released under [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0). If you use this register, please cite the GeoBON DOI `10.25829/xf8ek6` for the underlying data and the BioClima project for the register itself.
