import re
from typing import Any


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
