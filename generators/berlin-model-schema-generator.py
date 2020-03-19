import csv
import json
import hashlib


def const(value):
    return {"const": value, "default": value}


def generate_id(value):
    return hashlib.md5(str(value).encode("utf-8")).hexdigest()


def generate_attribute_id(attribute_sctid, symptom_id=None):
    return generate_id(
        f"{symptom_id}-{attribute_sctid}" if symptom_id is not None else attribute_sctid
    )


def object_template(id_raw, name, id_generator=lambda id_raw: generate_id(id_raw)):
    sctid = None
    custom_id = None
    if "CUSTOM:" in id_raw:
        custom_id = int(id_raw.split(":")[1])
    else:
        sctid = int(id_raw)
    id_ = id_generator(id_raw)

    object_ = {
        "type": "object",
        "title": name,
        "properties": {"id": const(id_), "name": const(name)},
        "required": ["id", "name"],
        "additionalProperties": False,
    }

    if sctid is not None:
        add_properties(object_, {"sctid": const(sctid)})

    if custom_id is not None:
        add_properties(object_, {"customId": const(custom_id)})

    return object_


def lookup(json_schema_object, property_name):
    return json_schema_object["properties"][property_name]["const"]


def add_properties(json_schema_object, properties: dict):
    for key, value in properties.items():
        json_schema_object["properties"][key] = value
        json_schema_object["required"].append(key)


def register_diagnosis(schema_json):
    with open("../berlin-model-source/diagnosis.csv", "r") as diagnosis_csv_file:
        diagnosis_csv = csv.reader(diagnosis_csv_file, delimiter=",")
        conditions = []
        for line_number, diagnosis in enumerate(diagnosis_csv):
            if line_number == 0:
                continue

            [condition_sctid_raw, condition_name] = diagnosis
            condition = object_template(condition_sctid_raw, condition_name)
            condition_id = lookup(condition, "id")

            schema_json["definitions"][condition_id] = condition

            conditions.append(
                {"title": condition_name, "$ref": f"#/definitions/{condition_id}",}
            )

        schema_json["definitions"]["condition"] = {"oneOf": conditions}


def register_symptoms_and_attributes(schema_json):
    with open(
        "../berlin-model-source/symptom-attributes.csv", "r"
    ) as symptom_attributes_csv_file:
        symptom_attributes_csv = csv.reader(symptom_attributes_csv_file, delimiter=",")
        symptoms = []
        attributes = []

        for line_number, diagnosis in enumerate(symptom_attributes_csv):
            if line_number == 0:
                continue

            [
                symptom_sctid_raw,
                symptom_name,
                attribute_sctid_raw,
                attribute_name,
                attributes_scoped_to_concept,
                has_value_set,
            ] = diagnosis

            attributes_scoped_to_concept = attributes_scoped_to_concept == "TRUE"

            if symptom_sctid_raw:
                current_symptom = object_template(symptom_sctid_raw, symptom_name)
                symptom_id = lookup(current_symptom, "id")
                add_properties(
                    current_symptom, {"state": {"$ref": "#/definitions/symptomState"}}
                )

                if attribute_sctid_raw:
                    current_symptom["properties"]["attributes"] = {
                        "type": "array",
                        "items": {"oneOf": []},  # attributes register themselves later
                        "uniqueItems": True,
                    }
                    current_symptom["required"].append("attributes")

                schema_json["definitions"][symptom_id] = current_symptom

                symptoms.append(
                    {"title": symptom_name, "$ref": f"#/definitions/{symptom_id}"}
                )

            if attribute_sctid_raw:
                attribute = object_template(
                    attribute_sctid_raw,
                    attribute_name,
                    id_generator=lambda raw_id: (
                        generate_attribute_id(raw_id, symptom_id)
                        if attributes_scoped_to_concept
                        else generate_attribute_id(raw_id)
                    ),
                )
                attribute_id = lookup(attribute, "id")
                add_properties(
                    attribute, {"value": {"oneOf": []}}
                )  # values register themselves later

                if attributes_scoped_to_concept:
                    attribute["properties"]["scope"] = const(symptom_id)

                schema_json["definitions"][attribute_id] = attribute

                attribute_ref = {
                    "title": attribute_name,
                    "$ref": f"#/definitions/{attribute_id}",
                }

                schema_json["definitions"][symptom_id]["properties"]["attributes"][
                    "items"
                ]["oneOf"].append(attribute_ref)

                attributes.append(attribute_ref)

        schema_json["definitions"]["symptom"] = {"oneOf": symptoms}
        # likely not necessary: attributes are never referenced generically, always explicitly by a linked symptom
        schema_json["definitions"]["attribute"] = {"oneOf": attributes}


def register_attribute_value_sets(schema_json):
    with open(
        "../berlin-model-source/attribute-value-sets.csv", "r"
    ) as attribute_value_sets_csv_file:
        attribute_value_sets_csv = csv.reader(
            attribute_value_sets_csv_file, delimiter=","
        )
        values = []

        for line_number, diagnosis in enumerate(attribute_value_sets_csv):
            if line_number == 0:
                continue

            [
                symptom_sctid_raw,
                symptom_name,
                attribute_sctid_raw,
                attribute_name,
                value_sctid_raw,
                value_name,
            ] = diagnosis

            if attribute_sctid_raw:
                current_attribute_id = (
                    generate_attribute_id(
                        attribute_sctid_raw, generate_id(symptom_sctid_raw)
                    )
                    if symptom_sctid_raw
                    else generate_attribute_id(attribute_sctid_raw)
                )

            value = object_template(
                value_sctid_raw,
                value_name,
                id_generator=lambda _: generate_id(
                    f"{current_attribute_id}-{value_sctid_raw}"
                ),
            )
            value_id = lookup(value, "id")
            schema_json["definitions"][value_id] = value

            value_ref = {"title": value_name, "$ref": f"#/definitions/{value_id}"}

            schema_json["definitions"][current_attribute_id]["properties"]["value"][
                "oneOf"
            ].append(value_ref)

            values.append(value_ref)

        # likely not necessary: values are never referenced generically, always explicitly by a linked attribute
        schema_json["definitions"]["value"] = {"oneOf": values}


def generate_berlin_model_schema():
    with open(
        "../schemas/berlin-model-generic.schema.json", "r"
    ) as base_schema_json_file:
        base_schema_json = json.load(base_schema_json_file)

    base_schema_json["$id"] = "http://example.com/berlin-model-generated.schema.json"
    base_schema_json[
        "description"
    ] = "FGAI4H TG Symptom Cases Schema – Berlin (generated)"
    base_schema_json[
        "$comment"
    ] = "This model is auto-generated! Don't manually make changes you wish to persist."

    register_diagnosis(base_schema_json)
    register_symptoms_and_attributes(base_schema_json)
    register_attribute_value_sets(base_schema_json)

    with open(
        "../schemas/berlin-model-generated.schema.json", "w"
    ) as generated_schema_json_file:
        json.dump(base_schema_json, generated_schema_json_file, indent=2)


if __name__ == "__main__":
    generate_berlin_model_schema()
