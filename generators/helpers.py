import hashlib


def create_const(value, description):
    return {"const": value, "default": value, "description": description}


def lookup_const(json_schema_object, property_name):
    return json_schema_object["properties"][property_name]["const"]


def generate_id(value):
    return hashlib.md5(str(value).encode("utf-8")).hexdigest()


def generate_attribute_id(attribute_sctid, symptom_id=None):
    return generate_id(
        f"{symptom_id}-{attribute_sctid}" if symptom_id is not None else attribute_sctid
    )


def concept_template(
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

    concept = {
        "type": "object",
        "title": name,
        "properties": {
            "id": create_const(id_, f"{concept_name} ID"),
            "name": create_const(name, f"{concept_name} name"),
        },
        "required": ["id", "name"],
        "additionalProperties": False,
    }

    if sctid is not None:
        add_properties(
            concept,
            {
                "sctid": create_const(
                    sctid, f"{concept_name} SNOMED CT identifier (64-bit integer)"
                )
            },
        )

    if custom_id is not None:
        add_properties(
            concept,
            {"customId": create_const(custom_id, f"{concept_name} custom identifier")},
        )

    return concept


def add_properties(json_schema_object, properties: dict):
    for key, value in properties.items():
        json_schema_object["properties"][key] = value
        json_schema_object["required"].append(key)
