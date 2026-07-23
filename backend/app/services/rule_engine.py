from dataclasses import dataclass
from typing import Any


class RuleEvaluationError(
    RuntimeError
):
    pass


@dataclass(frozen=True)
class RuleEvaluationResult:
    status: str
    awarded_score: float
    maximum_score: float

    requires_manual_review: bool

    warnings: list[str]


def evaluate_rule(
    *,
    rule_type: str,
    rule_config: dict[str, Any],
    extracted_values: dict[str, Any],
    maximum_score: float,
    evidence_status: str,
) -> RuleEvaluationResult:
    if evidence_status == "conflicting":
        return RuleEvaluationResult(
            status="manual_review",
            awarded_score=0,
            maximum_score=maximum_score,
            requires_manual_review=True,
            warnings=[
                "Kriter için çelişkili belge kanıtları bulundu."
            ],
        )

    if evidence_status in {
        "not_found",
        "ambiguous",
    }:
        return RuleEvaluationResult(
            status=str(
                rule_config.get(
                    "missing_result",
                    "uncertain",
                )
            ),
            awarded_score=0,
            maximum_score=maximum_score,
            requires_manual_review=(
                evidence_status == "ambiguous"
            ),
            warnings=[],
        )

    if rule_type == "evidence_presence":
        return _evaluate_evidence_presence(
            rule_config=rule_config,
            extracted_values=extracted_values,
            maximum_score=maximum_score,
        )

    if rule_type == "boolean_value":
        return _evaluate_boolean_value(
            rule_config=rule_config,
            extracted_values=extracted_values,
            maximum_score=maximum_score,
        )

    if rule_type in {
        "numeric_threshold",
        "percentage_threshold",
    }:
        return _evaluate_numeric_threshold(
            rule_config=rule_config,
            extracted_values=extracted_values,
            maximum_score=maximum_score,
        )

    if rule_type == "numeric_range":
        return _evaluate_numeric_range(
            rule_config=rule_config,
            extracted_values=extracted_values,
            maximum_score=maximum_score,
        )

    raise RuleEvaluationError(
        f"Desteklenmeyen kural türü: {rule_type}"
    )


def _evaluate_evidence_presence(
    *,
    rule_config: dict[str, Any],
    extracted_values: dict[str, Any],
    maximum_score: float,
) -> RuleEvaluationResult:
    field = str(rule_config["field"])

    value = extracted_values.get(field)

    passed = value not in {
        None,
        "",
        False,
    }

    return _build_binary_result(
        passed=passed,
        rule_config=rule_config,
        maximum_score=maximum_score,
    )


def _evaluate_boolean_value(
    *,
    rule_config: dict[str, Any],
    extracted_values: dict[str, Any],
    maximum_score: float,
) -> RuleEvaluationResult:
    field = str(rule_config["field"])

    actual = extracted_values.get(field)
    expected = rule_config.get("expected")

    if actual is None:
        return RuleEvaluationResult(
            status="uncertain",
            awarded_score=0,
            maximum_score=maximum_score,
            requires_manual_review=False,
            warnings=[
                f"{field} değeri belgelerden çıkarılamadı."
            ],
        )

    return _build_binary_result(
        passed=actual == expected,
        rule_config=rule_config,
        maximum_score=maximum_score,
    )


def _evaluate_numeric_threshold(
    *,
    rule_config: dict[str, Any],
    extracted_values: dict[str, Any],
    maximum_score: float,
) -> RuleEvaluationResult:
    field = str(rule_config["field"])

    unit_validation_result = _validate_unit(
        rule_config=rule_config,
        extracted_values=extracted_values,
        maximum_score=maximum_score,
    )

    if unit_validation_result is not None:
        return unit_validation_result

    raw_value = extracted_values.get(field)

    if raw_value is None:
        return RuleEvaluationResult(
            status="uncertain",
            awarded_score=0,
            maximum_score=maximum_score,
            requires_manual_review=False,
            warnings=[
                f"{field} sayısal değeri bulunamadı."
            ],
        )

    try:
        value = float(raw_value)
        threshold = float(
            rule_config["threshold"]
        )
    except (
        TypeError,
        ValueError,
        KeyError,
    ) as exc:
        raise RuleEvaluationError(
            "Sayısal kural değeri geçersiz."
        ) from exc

    operator = str(
        rule_config["operator"]
    )

    comparisons = {
        "less_than": value < threshold,
        "less_than_or_equal":
            value <= threshold,
        "greater_than":
            value > threshold,
        "greater_than_or_equal":
            value >= threshold,
        "equal": value == threshold,
    }

    if operator not in comparisons:
        raise RuleEvaluationError(
            f"Desteklenmeyen operatör: {operator}"
        )

    return _build_binary_result(
        passed=comparisons[operator],
        rule_config=rule_config,
        maximum_score=maximum_score,
    )


def _validate_unit(
    *,
    rule_config: dict[str, Any],
    extracted_values: dict[str, Any],
    maximum_score: float,
) -> RuleEvaluationResult | None:
    expected_unit = rule_config.get(
        "expected_unit"
    )
    unit_field = rule_config.get(
        "unit_field"
    )

    if not expected_unit or not unit_field:
        return None

    actual_unit = extracted_values.get(
        unit_field
    )

    if actual_unit == expected_unit:
        return None

    return RuleEvaluationResult(
        status="manual_review",
        awarded_score=0,
        maximum_score=maximum_score,
        requires_manual_review=True,
        warnings=[
            (
                "Belgedeki sayısal değer birimi "
                "kuralın beklediği birimle "
                "doğrulanamadı."
            )
        ],
    )


def _evaluate_numeric_range(
    *,
    rule_config: dict[str, Any],
    extracted_values: dict[str, Any],
    maximum_score: float,
) -> RuleEvaluationResult:
    field = str(rule_config["field"])
    raw_value = extracted_values.get(field)

    if raw_value is None:
        return RuleEvaluationResult(
            status="uncertain",
            awarded_score=0,
            maximum_score=maximum_score,
            requires_manual_review=False,
            warnings=[
                f"{field} değeri bulunamadı."
            ],
        )

    value = float(raw_value)
    minimum = float(rule_config["minimum"])
    maximum = float(rule_config["maximum"])

    return _build_binary_result(
        passed=minimum <= value <= maximum,
        rule_config=rule_config,
        maximum_score=maximum_score,
    )


def _build_binary_result(
    *,
    passed: bool,
    rule_config: dict[str, Any],
    maximum_score: float,
) -> RuleEvaluationResult:
    if passed:
        score = float(
            rule_config.get(
                "pass_score",
                maximum_score,
            )
        )

        return RuleEvaluationResult(
            status="satisfied",
            awarded_score=min(
                score,
                maximum_score,
            ),
            maximum_score=maximum_score,
            requires_manual_review=False,
            warnings=[],
        )

    score = float(
        rule_config.get(
            "fail_score",
            0,
        )
    )

    return RuleEvaluationResult(
        status="not_satisfied",
        awarded_score=min(
            score,
            maximum_score,
        ),
        maximum_score=maximum_score,
        requires_manual_review=False,
        warnings=[],
    )
