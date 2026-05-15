
# Kunming-Montreal GBF Target (Schema)

`ogc.bioclima.policy.kmgbf-target` *v0.1.0*

Schema for a single target of the Kunming-Montreal Global Biodiversity Framework: target number, multilingual label and definition, deadline, key indicators.

[*Status*](http://www.opengis.net/def/status): Under development

## Description

# Kunming-Montreal GBF Target

Schema for one of the 23 targets of the Kunming-Montreal Global Biodiversity Framework. Each target carries a multilingual label, definition, deadline and the list of indicators that report against it.

## Examples

### KMGBF Target 8 - Climate change adaptation
A concrete target record.
#### json
```json
{
  "id": "https://maytetoscano.github.io/Bioclima_OGC/ontology/policy/kmgbf-target-8",
  "targetNumber": 8,
  "label": {
    "en": "Climate change adaptation",
    "es": "Adaptación al cambio climático",
    "zh": "气候变化适应",
    "ro": "Adaptare la schimbările climatice"
  },
  "definition": {
    "en": "Minimize the impact of climate change on biodiversity through mitigation, adaptation and disaster risk reduction actions, including through nature-based solutions and/or ecosystem-based approaches.",
    "es": "Minimizar el impacto del cambio climático sobre la biodiversidad mediante acciones de mitigación, adaptación y reducción del riesgo de desastres, incluso mediante soluciones basadas en la naturaleza y/o enfoques basados en los ecosistemas.",
    "zh": "通过减缓、适应和减少灾害风险的行动,包括基于自然的解决方案和/或基于生态系统的方法,尽量减少气候变化对生物多样性的影响。",
    "ro": "Minimizarea impactului schimbărilor climatice asupra biodiversității prin acțiuni de atenuare, adaptare și reducere a riscului de dezastre, inclusiv prin soluții bazate pe natură și/sau abordări bazate pe ecosisteme."
  },
  "deadline": "2030-12-31",
  "keyIndicators": [
    "https://maytetoscano.github.io/Bioclima_OGC/ontology/indicator/pci"
  ],
  "source": "https://www.cbd.int/doc/decisions/cop-15/cop-15-dec-04-en.pdf"
}
```

## Schema

```yaml
$schema: https://json-schema.org/draft/2020-12/schema
$id: https://maytetoscano.github.io/Bioclima_OGC/bblock/ogc.bioclima.policy.kmgbf-target/schema.yaml
title: KMGBF Target
type: object
required:
- id
- targetNumber
- label
- definition
properties:
  id:
    type: string
    format: iri
  targetNumber:
    type: integer
    minimum: 1
    maximum: 23
  label:
    type: object
    required:
    - en
  definition:
    type: object
    required:
    - en
  deadline:
    type: string
    format: date
  keyIndicators:
    type: array
    items:
      type: string
      format: iri
  source:
    type: string
    format: iri

```

Links to the schema:

* YAML version: [schema.yaml](https://maytetoscano.github.io/Bioclima_OGC/build/annotated/bioclima/policy/kmgbf-target/schema.json)
* JSON version: [schema.json](https://maytetoscano.github.io/Bioclima_OGC/build/annotated/bioclima/policy/kmgbf-target/schema.yaml)


# For developers

The source code for this Building Block can be found in the following repository:

* URL: [https://github.com/MayteToscano/Bioclima_OGC](https://github.com/MayteToscano/Bioclima_OGC)
* Path: `_sources/policy/kmgbf-target`

