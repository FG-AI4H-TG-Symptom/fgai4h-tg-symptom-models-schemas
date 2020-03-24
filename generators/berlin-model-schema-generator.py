import csv
import json
import hashlib


def const(value, description):
    return {"const": value, "default": value, "description": description}


def generate_id(value):
    return hashlib.md5(str(value).encode("utf-8")).hexdigest()


def generate_attribute_id(attribute_sctid, symptom_id=None):
    return generate_id(
        f"{symptom_id}-{attribute_sctid}" if symptom_id is not None else attribute_sctid
    )


def object_template(
    concept_name: str,
    id_raw: str,
    name: str,
    id_generator=lambda id_raw: generate_id(id_raw),
):
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
        "properties": {
            "id": const(id_, f"{concept_name} ID"),
            "name": const(name, f"{concept_name} name"),
        },
        "required": ["id", "name"],
        "additionalProperties": False,
    }

    if sctid is not None:
        add_properties(
            object_,
            {
                "sctid": const(
                    sctid, f"{concept_name} SNOMED CT identifier (64-bit integer)"
                )
            },
        )

    if custom_id is not None:
        add_properties(
            object_, {"customId": const(custom_id, f"{concept_name} custom identifier")}
        )

    return object_


def lookup(json_schema_object, property_name):
    return json_schema_object["properties"][property_name]["const"]


def add_properties(json_schema_object, properties: dict):
    for key, value in properties.items():
        json_schema_object["properties"][key] = value
        json_schema_object["required"].append(key)


def register_diagnosis(schema_json):
    with open("../berlin-model-source/conditions.csv", "r") as conditions_csv_file:
        conditions_csv = csv.reader(conditions_csv_file, delimiter=",")
        conditions = []
        for line_number, entry in enumerate(conditions_csv):
            if line_number == 0:
                continue

            [condition_sctid_raw, condition_name] = entry
            condition = object_template(
                "Condition", condition_sctid_raw, condition_name
            )
            condition_id = lookup(condition, "id")

            schema_json["definitions"][condition_id] = condition

            conditions.append(
                {"title": condition_name, "$ref": f"#/definitions/{condition_id}",}
            )

        schema_json["definitions"]["condition"] = {"oneOf": conditions}


def register_clinical_findings_and_attributes(schema_json):
    with open(
        "../berlin-model-source/clinical_findings-attributes.csv", "r"
    ) as clinical_findings_attributes_csv_file:
        clinical_findings_attributes_csv = csv.reader(
            clinical_findings_attributes_csv_file, delimiter=","
        )
        clinical_findings = []
        attributes = []

        for line_number, entry in enumerate(clinical_findings_attributes_csv):
            if line_number == 0:
                continue

            [
                clinical_finding_sctid_raw,
                clinical_finding_name,
                attribute_sctid_raw,
                attribute_name,
                attribute_scoped_to_clinical_finding,
            ] = entry

            attribute_scoped_to_clinical_finding = (
                attribute_scoped_to_clinical_finding == "TRUE"
            )

            if clinical_finding_sctid_raw:
                current_clinical_finding = object_template(
                    "Clinical finding",
                    clinical_finding_sctid_raw,
                    clinical_finding_name,
                )
                clinical_finding_id = lookup(current_clinical_finding, "id")

                add_properties(
                    current_clinical_finding,
                    {"state": {"$ref": "#/definitions/clinicalFindingState"}},
                )

                if attribute_sctid_raw:
                    current_clinical_finding["properties"]["attributes"] = {
                        "type": "array",
                        "items": {"oneOf": []},  # attributes register themselves later
                        "uniqueItems": True,
                    }
                    current_clinical_finding["required"].append("attributes")

                schema_json["definitions"][
                    clinical_finding_id
                ] = current_clinical_finding

                clinical_findings.append(
                    {
                        "title": clinical_finding_name,
                        "$ref": f"#/definitions/{clinical_finding_id}",
                    }
                )

            if attribute_sctid_raw:
                attribute = object_template(
                    "Attribute",
                    attribute_sctid_raw,
                    attribute_name,
                    id_generator=lambda raw_id: (
                        generate_attribute_id(raw_id, clinical_finding_id)
                        if attribute_scoped_to_clinical_finding
                        else generate_attribute_id(raw_id)
                    ),
                )
                attribute_id = lookup(attribute, "id")
                add_properties(
                    attribute, {"value": {"oneOf": []}}
                )  # values register themselves later

                already_registered_attribute = schema_json["definitions"].get(
                    attribute_id, None
                )

                attribute_ref = {
                    "title": attribute_name
                    if already_registered_attribute is None
                    else lookup(already_registered_attribute, "name"),
                    "$ref": f"#/definitions/{attribute_id}",
                }

                schema_json["definitions"][clinical_finding_id]["properties"][
                    "attributes"
                ]["items"]["oneOf"].append(attribute_ref)

                if already_registered_attribute is not None:
                    print(
                        f"Attribute '{attribute_id}' ({attribute_sctid_raw} '{attribute_name}') "
                        f"already defined, skipping."
                    )
                    continue

                if attribute_scoped_to_clinical_finding:
                    attribute["properties"]["scope"] = const(
                        clinical_finding_id,
                        "ID of clinical finding this attribute is scoped to",
                    )

                schema_json["definitions"][attribute_id] = attribute

                attributes.append(attribute_ref)

        schema_json["definitions"]["clinicalFinding"] = {"oneOf": clinical_findings}
        # likely not necessary: attributes are never referenced generically, always explicitly by a linked symptom
        schema_json["definitions"]["attribute"] = {"oneOf": attributes}


def register_attribute_value_sets(schema_json):
    with open(
        "../berlin-model-source/attributes-value_sets.csv", "r"
    ) as attribute_value_sets_csv_file:
        attribute_value_sets_csv = csv.reader(
            attribute_value_sets_csv_file, delimiter=","
        )
        values = []

        for line_number, entry in enumerate(attribute_value_sets_csv):
            if line_number == 0:
                continue

            [
                clinical_finding_sctid_raw,
                clinical_finding_name,
                attribute_sctid_raw,
                attribute_name,
                value_sctid_raw,
                value_name,
            ] = entry

            if attribute_sctid_raw:
                current_attribute_id = (
                    generate_attribute_id(
                        attribute_sctid_raw, generate_id(clinical_finding_sctid_raw)
                    )
                    if clinical_finding_sctid_raw
                    else generate_attribute_id(attribute_sctid_raw)
                )

            value = object_template(
                "Value",
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

    base_schema_json["$id"] = (
        "https://raw.githubusercontent.com/FG-AI4H-TG-Symptom/"
        "fgai4h-tg-symptom-models-schemas/master/schemas/berlin-model-generated.schema.json"
    )
    base_schema_json[
        "description"
    ] = "FGAI4H TG Symptom Cases Schema – Berlin (generated)"
    base_schema_json[
        "$comment"
    ] = "This model is auto-generated! Don't manually make changes you wish to persist."

    register_diagnosis(base_schema_json)
    register_clinical_findings_and_attributes(base_schema_json)
    register_attribute_value_sets(base_schema_json)

    with open(
        "../schemas/berlin-model-generated.schema.json", "w"
    ) as generated_schema_json_file:
        json.dump(base_schema_json, generated_schema_json_file, indent=2)


if __name__ == "__main__":
    generate_berlin_model_schema()
