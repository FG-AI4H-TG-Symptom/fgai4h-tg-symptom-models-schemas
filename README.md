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

Two schemas exist at the moment:

- `schemas/berlin-model.schema.json`, a software-generated model aiming to accurately represent relationships  
  Online reference: `https://raw.githubusercontent.com/FG-AI4H-TG-Symptom/fgai4h-tg-symptom-models-schemas/master/schemas/berlin-model.schema.json`
- `schemas/berlin-model-generic.schema.json`, a hand-written version aiming to be a compatible super-set of the generated version by replacing all constants with types  
  Online reference: `https://raw.githubusercontent.com/FG-AI4H-TG-Symptom/fgai4h-tg-symptom-models-schemas/master/schemas/berlin-model-generic.schema.json`

Put differently: the generic schema is the foundation for the generated schema. Everything valid under the generated schema must be valid under the generic schema, but not vice versa. The generated schema introduces constraints, nothing else.

You can explore the the (generated) schema [with this tool](https://fg-ai4h-tg-symptom.github.io/fgai4h-tg-symptom-models-schemas/),
although it is a bit cumbersome and sometimes buggy.

The generator resides in `generators/berlin-model-schema-generator.py` and consumes the CSV sheets in `berlin-model-source/*.csv`.

The CSV sheets are based on Alejandro Lopez Osornio's interoperability model.
They can be found [here](https://docs.google.com/spreadsheets/d/1fbFNh-vpqlIljIg2OMlXmLCbqeV9ISL4eRaepW0jmjo),
or downloaded automatically by executing `berlin-model-source/download-csv.py`

### Cases

A proof-of-concept case exists in `cases/berlin-cases-generated.json` and should validate against `schemas/berlin-model.schema.json` (NB the case is still written by hand).

The source is [this sheet](https://docs.google.com/spreadsheets/d/111D40yoJqvvHZEYI8RNSnemGf0abC9hQjQ7crFzNrdk/edit#gid=824759292).

## Code

This repository is aimed at a recent version of Python 3 and uses `black` for formatting.

Models should use camelCase identifiers. (Python could should use snake_case where possible.)
