import csv
import json

from generators.helpers import (
    create_const,
    lookup_const,
    generate_id,
    concept_template,
    add_properties,
)


def register_diagnosis(schema_json):
    with open("../berlin-model-source/conditions.csv", "r") as conditions_csv_file:
        conditions_csv = csv.reader(conditions_csv_file, delimiter=",")
        conditions = []
        for line_number, entry in enumerate(conditions_csv):
            if line_number == 0:
                continue

            [condition_sctid_raw, condition_name] = entry
            condition = concept_template(
                "Condition", condition_sctid_raw, condition_name
            )
            condition_id = lookup_const(condition, "id")

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
                attribute_value_multi_select,
            ] = entry

            attribute_scoped_to_clinical_finding = (
                attribute_scoped_to_clinical_finding == "TRUE"
            )

            if clinical_finding_sctid_raw:
                current_clinical_finding = concept_template(
                    "Clinical finding",
                    clinical_finding_sctid_raw,
                    clinical_finding_name,
                )
                clinical_finding_id = lookup_const(current_clinical_finding, "id")

                add_properties(
                    current_clinical_finding,
                    {"state": {"$ref": "#/definitions/clinicalFindingState"}},
                )

                if attribute_sctid_raw:
                    add_properties(
                        current_clinical_finding,
                        {
                            "attributes": {
                                "type": "array",
                                "items": {
                                    "oneOf": []
                                },  # attributes register themselves later
                                "uniqueItems": True,
                            }
                        },
                    )

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
                attribute = concept_template(
                    "Attribute",
                    attribute_sctid_raw,
                    attribute_name,
                    scope=(clinical_finding_id if attribute_scoped_to_clinical_finding else None)
                )
                attribute_id = lookup_const(attribute, "id")
                if attribute_value_multi_select == "MULTI":
                    # values register themselves later
                    add_properties(
                        attribute,
                        {
                            "values": {
                                "type": "array",
                                "description": "Possible values for this attribute "
                                "(at least one, multi-selection possible)",
                                "items": {"oneOf": []},
                                "uniqueItems": True,
                                "minItems": 1,
                            }
                        },
                    )
                else:
                    # values register themselves later
                    add_properties(
                        attribute,
                        {
                            "value": {
                                "description": "Possible values for this attribute (exactly one)",
                                "oneOf": [],
                            }
                        },
                    )

                already_registered_attribute = schema_json["definitions"].get(
                    attribute_id, None
                )

                attribute_ref = {
                    "title": attribute_name
                    if already_registered_attribute is None
                    else lookup_const(already_registered_attribute, "name"),
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
                    attribute["properties"]["scope"] = create_const(
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
                current_attribute_id = generate_id(
                    "Attribute",
                    attribute_name,
                    generate_id("Clinical finding", clinical_finding_name)
                    if clinical_finding_sctid_raw
                    and clinical_finding_sctid_raw != "ANY"
                    else None,
                )

            value = concept_template(
                "Value",
                value_sctid_raw,
                value_name,
                scope=f"{current_attribute_id}",
            )
            value_id = lookup_const(value, "id")
            schema_json["definitions"][value_id] = value

            value_ref = {"title": value_name, "$ref": f"#/definitions/{value_id}"}

            attribute_properties = schema_json["definitions"][current_attribute_id][
                "properties"
            ]
            attribute_value_list = (
                attribute_properties["values"]["items"]["oneOf"]
                if "values" in attribute_properties
                else attribute_properties["value"]["oneOf"]
            )
            attribute_value_list.append(value_ref)

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
        "fgai4h-tg-symptom-models-schemas/master/schemas/berlin-model.schema.json"
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

    with open("../schemas/berlin-model.schema.json", "w") as generated_schema_json_file:
        json.dump(base_schema_json, generated_schema_json_file, indent=2)


if __name__ == "__main__":
    generate_berlin_model_schema()
