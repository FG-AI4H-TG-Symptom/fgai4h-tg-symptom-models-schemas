import hashlib
from typing import Optional


def create_const(value, description):
    return {"const": value, "default": value, "description": description}


def lookup_const(json_schema_object, property_name):
    return json_schema_object["properties"][property_name]["const"]


def generate_id(concept_name: str, name: str, scope: Optional[str] = None) -> str:
    name = name[:name.find('(')].strip() if '(' in name else name
    return (concept_name + "@" + name).lower().replace(" ", "_").replace("/", "-") + (
        "$" + scope if scope else ""
    )


def concept_template(
    concept_name: str,
    id_raw: str,
    name: str,
    scope: Optional[str] = None,
):
    sctid = None
    if "CUSTOM" not in id_raw:
        sctid = int(id_raw)
    id_ = generate_id(concept_name, name, scope)

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

    return concept


def add_properties(json_schema_object, properties: dict):
    for key, value in properties.items():
        json_schema_object["properties"][key] = value
        json_schema_object["required"].append(key)
