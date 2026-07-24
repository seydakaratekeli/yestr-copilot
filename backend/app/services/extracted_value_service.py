import re
from typing import Any


_UNIT_ALIASES: dict[str, set[str]] = {
    "L/min": {
        "l/min",
        "l/dak",
        "l/dk",
        "l/dakika",
        "litre/dak",
        "litre/dk",
        "litre/dakika",
        "liter/dak",
        "liter/dk",
        "liter/dakika",
    },
    "L/s": {
        "l/s",
        "l/sn",
        "l/saniye",
        "litre/sn",
        "litre/saniye",
        "liter/sn",
        "liter/saniye",
    },
    "m³/h": {
        "m3/h",
        "m³/h",
        "m3/saat",
        "m³/saat",
    },
    "kW": {"kw", "kilowatt"},
    "W": {"w", "watt"},
}


def normalize_extracted_values(
    *,
    rule_config: dict[str, Any],
    extracted_values: dict[str, Any],
) -> dict[str, Any]:
    normalized = dict(extracted_values)

    field = rule_config.get("field")

    if not field:
        return normalized

    value = normalized.get(field)

    if isinstance(value, str):
        number = extract_first_number(value)

        if number is not None:
            normalized[field] = number

    unit_field = rule_config.get("unit_field")
    expected_unit = rule_config.get("expected_unit")

    if unit_field and expected_unit:
        actual_unit = normalized.get(unit_field)

        if isinstance(actual_unit, str):
            normalized[unit_field] = (
                normalize_unit(
                    actual_unit=actual_unit,
                    expected_unit=str(expected_unit),
                )
            )

    return normalized


def extract_first_number(
    value: str,
) -> float | None:
    match = re.search(
        r"-?\d+(?:[.,]\d+)?",
        value,
    )

    if not match:
        return None

    normalized_number = (
        match.group(0).replace(",", ".")
    )

    try:
        return float(normalized_number)

    except ValueError:
        return None


def normalize_unit(
    *,
    actual_unit: str,
    expected_unit: str,
) -> str:
    actual_key = _normalize_unit_key(
        actual_unit
    )
    expected_key = _normalize_unit_key(
        expected_unit
    )

    for canonical_unit, aliases in (
        _UNIT_ALIASES.items()
    ):
        normalized_aliases = {
            _normalize_unit_key(alias)
            for alias in aliases
        }
        normalized_aliases.add(
            _normalize_unit_key(canonical_unit)
        )

        if (
            expected_key in normalized_aliases
            and actual_key in normalized_aliases
        ):
            return expected_unit

    if actual_key == expected_key:
        return expected_unit

    return actual_unit.strip()


def _normalize_unit_key(
    value: str,
) -> str:
    return re.sub(
        r"\s+",
        "",
        value.strip().casefold(),
    )
