from app.services.criterion_evidence_service import (
    _build_extracted_values_schema,
)


def test_numeric_rule_builds_closed_nullable_schema():
    schema = _build_extracted_values_schema(
        expected_field="installed_power_kw",
        rule_type="numeric_threshold",
        unit_field="installed_power_unit",
    )

    assert schema == {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "installed_power_kw": {
                "type": ["number", "null"],
            },
            "installed_power_unit": {
                "type": ["string", "null"],
            },
        },
        "required": [
            "installed_power_kw",
            "installed_power_unit",
        ],
    }


def test_boolean_rule_builds_closed_nullable_schema():
    schema = _build_extracted_values_schema(
        expected_field="has_rainwater_storage",
        rule_type="boolean_value",
    )

    assert schema["additionalProperties"] is False
    assert schema["properties"] == {
        "has_rainwater_storage": {
            "type": ["boolean", "null"],
        },
    }
    assert schema["required"] == [
        "has_rainwater_storage"
    ]


def test_rule_without_field_builds_empty_closed_schema():
    schema = _build_extracted_values_schema(
        expected_field="",
        rule_type="evidence_presence",
    )

    assert schema == {
        "type": "object",
        "additionalProperties": False,
        "properties": {},
        "required": [],
    }
