import hashlib
from typing import Optional


def create_const(value, description):
    return {"const": value, "default": value, "description": description}


def lookup_const(json_schema_object, property_name):
    return json_schema_object["properties"][property_name]["const"]


def generate_id(concept_name: str, concept_id: str, scope: Optional[str] = None) -> str:
    id_source = (
        concept_name.lower().replace(" ", "_")
        + ":"
        + concept_id
        + ("|" + scope if scope else "")
    )
    return hashlib.md5(id_source.encode("utf-8")).hexdigest()


def concept_template(
    concept_name: str, id_raw: str, name: str, scope: Optional[str] = None,
):
    sctid = None
    custom_id = None
    if "CUSTOM:" in id_raw:
        custom_id = int(id_raw.split(":")[1])
    else:
        sctid = int(id_raw)
    id_ = generate_id(concept_name, id_raw, scope)

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
