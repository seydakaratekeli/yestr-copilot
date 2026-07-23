from app.services.extracted_value_service import (
    extract_first_number,
    normalize_extracted_values,
)


def test_normalizes_number_with_unit():
    result = normalize_extracted_values(
        rule_config={
            "field": "maximum_flow_rate_l_min",
        },
        extracted_values={
            "maximum_flow_rate_l_min": "5 L/dakika",
        },
    )

    assert result == {
        "maximum_flow_rate_l_min": 5.0,
    }


def test_normalizes_decimal_comma_and_negative_value():
    assert extract_first_number(
        "ölçüm: -12,5 °C"
    ) == -12.5


def test_preserves_text_without_number():
    values = {
        "facade_insulation_evidence": (
            "Isı yalıtımı uygulanacaktır."
        ),
    }

    result = normalize_extracted_values(
        rule_config={
            "field": "facade_insulation_evidence",
        },
        extracted_values=values,
    )

    assert result == values
    assert result is not values


def test_preserves_values_when_field_is_not_configured():
    values = {
        "maximum_flow_rate_l_min": "5 L/dakika",
    }

    result = normalize_extracted_values(
        rule_config={},
        extracted_values=values,
    )

    assert result == values


def test_returns_none_when_number_is_absent():
    assert extract_first_number(
        "sayısal değer bulunamadı"
    ) is None
