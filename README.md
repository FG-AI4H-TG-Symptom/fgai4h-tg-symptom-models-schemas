# FGAI4H TG Symptom – Models & Schemas

## London model

The London model is finalized. 

The source can be found in [this sheet](https://docs.google.com/spreadsheets/d/111D40yoJqvvHZEYI8RNSnemGf0abC9hQjQ7crFzNrdk/edit#gid=575520860).

### Schema

Find the schema in `schemas/london-model.schema.json`.

### Cases

Find the cases in `cases/london-cases.json`; they validate against the schema.

The source is [this sheet](https://docs.google.com/spreadsheets/d/111D40yoJqvvHZEYI8RNSnemGf0abC9hQjQ7crFzNrdk/edit#gid=1175944267).

## Berlin model

The Berlin model is work-in-progress, the schema may change at any moment.

The source can be found in [this sheet](https://docs.google.com/spreadsheets/d/111D40yoJqvvHZEYI8RNSnemGf0abC9hQjQ7crFzNrdk/edit#gid=980125545). 

### Schema

Three schemas exist at the moment:

- `schemas/berlin-model-manual.schema.json`, a hand-written first attempt to create a schema
- `schemas/berlin-model-generated.schema.json`, a software-generated model aiming to accurately represent relationships
- `schemas/berlin-model-generic.schema.json`, a hand-written version aiming to be a compatible super-set of the generated version by replacing all constants with types

Put differently: the generic schema is the foundation for the generated schema. Everything valid under the generated schema must be valid under the generic schema, but not vice versa. The generated schema introduces constraints, nothing else.

The generator resides in `generators/berlin-model-schema-generator.py` and consumes the CSV sheets in `berlin-model-source/*.csv`.

The CSV sheets are based on Alejandro Lopez Osornio's interoperability model. 
Find the most relevant sheets here: [conditions](https://docs.google.com/spreadsheets/d/1dWXYWkn0h6je13zVEnSK0Bi14BsvqK2EXrrnv89Yge0/edit#gid=0),
[symptoms–attributes](https://docs.google.com/spreadsheets/d/1dWXYWkn0h6je13zVEnSK0Bi14BsvqK2EXrrnv89Yge0/edit#gid=1243051470),
[attributes–value sets](https://docs.google.com/spreadsheets/d/1dWXYWkn0h6je13zVEnSK0Bi14BsvqK2EXrrnv89Yge0/edit#gid=1283340500).

### Cases

Find the preliminary cases in `cases/berlin-cases.json`. They validate against `schemas/berlin-model-manual.schema.json`.

A proof-of-concept case based on the generated schema (`schemas/berlin-model-generated.schema.json`) exists in `cases/berlin-cases-generated.json` (NB the case is still written by hand).

The source is [this sheet](https://docs.google.com/spreadsheets/d/111D40yoJqvvHZEYI8RNSnemGf0abC9hQjQ7crFzNrdk/edit#gid=824759292).

## Code

This repository is aimed at a recent version of Python 3 and uses `black` for formatting.

Models should use camelCase identifiers. (Python could should use snake_case where possible.)
