
# Indicator Provenance (W3C PROV) (Schema)

`ogc.bioclima.provenance.indicator-provenance` *v0.1.0*

PROV-O record for a computed indicator: references EBV inputs, the Python implementation by URL, the git commit hash and the GitHub Actions run id.

[*Status*](http://www.opengis.net/def/status): Under development

## Description

# Indicator Provenance

PROV-O record for a computed indicator. Captures the input EBV bblocks, the implementation script URL, its git commit hash, the GitHub Actions run id and the numerical parameters used. Generated automatically by `recompute-indicators.yml`.

## Examples

### PCI provenance
Provenance record for the PCI computation.
#### json
```json
{
  "@context": {
    "@vocab": "http://www.w3.org/ns/prov#"
  },
  "entity": "ogc.bioclima.indicator.pci/examples/pci-finland-2001-2018.covjson",
  "wasDerivedFrom": [
    "ogc.bioclima.ebv.vap-coniferous",
    "ogc.bioclima.ebv.vap-deciduous"
  ],
  "wasGeneratedBy": {
    "activity": "Compute PCI from VAP-DOY cubes",
    "script": "https://maytetoscano.github.io/Bioclima_OGC/_sources/indicator/pci/code/compute.py",
    "scriptVersion": "095f7bf20f0abcf8dffe01ccba94bbd0ebb24ec9",
    "startedAtTime": "2024-11-01T12:00:00Z",
    "endedAtTime": "2026-05-15T13:32:09Z",
    "parameters": {
      "coniferous_weight": 0.4,
      "deciduous_weight": 0.6,
      "trend_method": "ordinary-least-squares",
      "min_valid_years": 8
    },
    "runId": "25920570793"
  },
  "wasAttributedTo": {
    "agent": "github://maytetoscano/Bioclima_OGC/.github/workflows/recompute-indicators.yml",
    "role": "Software agent"
  }
}
```

## Schema

```yaml
$schema: https://json-schema.org/draft/2020-12/schema
$id: https://maytetoscano.github.io/Bioclima_OGC/bblock/ogc.bioclima.provenance.indicator-provenance/schema.yaml
title: Indicator Provenance
allOf:
- $ref: https://maytetoscano.github.io/Bioclima_OGC/build/annotated/bioclima/provenance/ebv-provenance/schema.yaml
- type: object
  properties:
    wasGeneratedBy:
      type: object
      required:
      - script
      - scriptVersion
      properties:
        script:
          type: string
          format: iri
        scriptVersion:
          type: string
        runId:
          type: string
        parameters:
          type: object

```

Links to the schema:

* YAML version: [schema.yaml](https://maytetoscano.github.io/Bioclima_OGC/build/annotated/bioclima/provenance/indicator-provenance/schema.json)
* JSON version: [schema.json](https://maytetoscano.github.io/Bioclima_OGC/build/annotated/bioclima/provenance/indicator-provenance/schema.yaml)


# For developers

The source code for this Building Block can be found in the following repository:

* URL: [https://github.com/MayteToscano/Bioclima_OGC](https://github.com/MayteToscano/Bioclima_OGC)
* Path: `_sources/provenance/indicator-provenance`

