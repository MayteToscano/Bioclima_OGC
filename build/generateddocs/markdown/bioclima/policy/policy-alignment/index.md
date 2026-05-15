
# Indicator to Policy Alignment (Schema)

`ogc.bioclima.policy.policy-alignment` *v0.1.0*

Describes how a BioClima indicator aligns with KMGBF targets or SDGs: relationship type (informs, measures-progress-on, triggers-action-for, supports-reporting-on), evidence strength and multilingual justification.

[*Status*](http://www.opengis.net/def/status): Under development

## Description

# Indicator to Policy Alignment

Declares how an indicator aligns with one or more policy targets, with a relationship type, evidence strength and multilingual justification.

## Relationship types

- `measures-progress-on`
- `informs`
- `triggers-action-for`
- `supports-reporting-on`

## Examples

### PCI policy alignment
How the PCI aligns with KMGBF targets and SDG 15.
#### json
```json
{
  "indicator": "https://maytetoscano.github.io/Bioclima_OGC/ontology/indicator/pci",
  "alignments": [
    {
      "target": "https://maytetoscano.github.io/Bioclima_OGC/ontology/policy/kmgbf-target-8",
      "relationship": "measures-progress-on",
      "evidenceStrength": "direct",
      "justification": {
        "en": "Earlier or later onset of the growing season is a primary ecological signal of climate change pressure on boreal ecosystems; PCI quantifies that shift directly.",
        "es": "El adelanto o retraso del inicio del periodo vegetativo es una señal ecológica primaria de la presión del cambio climático sobre los ecosistemas boreales; el PCI lo cuantifica directamente.",
        "zh": "生长季开始的提前或延迟是气候变化对北方生态系统压力的主要生态信号;PCI 直接量化了这种变化。",
        "ro": "Avansul sau întârzierea începutului sezonului de creștere este un semnal ecologic principal al presiunii schimbărilor climatice asupra ecosistemelor boreale; PCI cuantifică această schimbare direct."
      }
    },
    {
      "target": "https://maytetoscano.github.io/Bioclima_OGC/ontology/policy/sdg-15",
      "relationship": "supports-reporting-on",
      "evidenceStrength": "contextual",
      "justification": {
        "en": "Phenological monitoring is widely accepted as part of the evidence base for SDG 15 reporting on the integrity of terrestrial ecosystems.",
        "es": "El seguimiento fenológico está ampliamente aceptado como parte de la base de evidencia para los informes del ODS 15 sobre la integridad de los ecosistemas terrestres.",
        "zh": "物候监测被广泛接受为可持续发展目标 15 关于陆地生态系统完整性报告的证据基础的一部分。",
        "ro": "Monitorizarea fenologică este larg acceptată ca parte din baza de dovezi pentru raportarea ODD 15 privind integritatea ecosistemelor terestre."
      }
    }
  ]
}
```

## Schema

```yaml
$schema: https://json-schema.org/draft/2020-12/schema
$id: https://maytetoscano.github.io/Bioclima_OGC/bblock/ogc.bioclima.policy.policy-alignment/schema.yaml
title: Policy Alignment
type: object
required:
- indicator
- alignments
properties:
  indicator:
    type: string
    format: iri
  alignments:
    type: array
    minItems: 1
    items:
      type: object
      required:
      - target
      - relationship
      properties:
        target:
          type: string
          format: iri
        relationship:
          enum:
          - informs
          - measures-progress-on
          - triggers-action-for
          - supports-reporting-on
        evidenceStrength:
          enum:
          - direct
          - indirect
          - contextual
        justification:
          type: object

```

Links to the schema:

* YAML version: [schema.yaml](https://maytetoscano.github.io/Bioclima_OGC/build/annotated/bioclima/policy/policy-alignment/schema.json)
* JSON version: [schema.json](https://maytetoscano.github.io/Bioclima_OGC/build/annotated/bioclima/policy/policy-alignment/schema.yaml)


# For developers

The source code for this Building Block can be found in the following repository:

* URL: [https://github.com/MayteToscano/Bioclima_OGC](https://github.com/MayteToscano/Bioclima_OGC)
* Path: `_sources/policy/policy-alignment`

