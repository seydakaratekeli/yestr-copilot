from app.services.rule_engine import (
    evaluate_rule,
)


def test_numeric_threshold_passes():
    result = evaluate_rule(
        rule_type="numeric_threshold",
        rule_config={
            "field":
                "maximum_flow_rate_l_min",
            "operator":
                "less_than_or_equal",
            "threshold": 5,
            "pass_score": 3,
            "fail_score": 0,
        },
        extracted_values={
            "maximum_flow_rate_l_min": 5
        },
        maximum_score=3,
        evidence_status="found",
    )

    assert result.status == "satisfied"
    assert result.awarded_score == 3


def test_numeric_threshold_fails():
    result = evaluate_rule(
        rule_type="numeric_threshold",
        rule_config={
            "field":
                "maximum_flow_rate_l_min",
            "operator":
                "less_than_or_equal",
            "threshold": 5,
            "pass_score": 3,
            "fail_score": 0,
        },
        extracted_values={
            "maximum_flow_rate_l_min": 8
        },
        maximum_score=3,
        evidence_status="found",
    )

    assert result.status == "not_satisfied"
    assert result.awarded_score == 0


def test_numeric_threshold_accepts_expected_unit():
    result = evaluate_rule(
        rule_type="numeric_threshold",
        rule_config={
            "field": "maximum_flow_rate_l_min",
            "unit_field": "maximum_flow_rate_unit",
            "expected_unit": "L/min",
            "operator": "less_than_or_equal",
            "threshold": 5,
            "pass_score": 3,
            "fail_score": 0,
        },
        extracted_values={
            "maximum_flow_rate_l_min": 5,
            "maximum_flow_rate_unit": "L/min",
        },
        maximum_score=3,
        evidence_status="found",
    )

    assert result.status == "satisfied"
    assert result.awarded_score == 3


def test_numeric_threshold_rejects_value_above_limit():
    result = evaluate_rule(
        rule_type="numeric_threshold",
        rule_config={
            "field": "maximum_flow_rate_l_min",
            "unit_field": "maximum_flow_rate_unit",
            "expected_unit": "L/min",
            "operator": "less_than_or_equal",
            "threshold": 5,
            "pass_score": 3,
            "fail_score": 0,
        },
        extracted_values={
            "maximum_flow_rate_l_min": 8,
            "maximum_flow_rate_unit": "L/min",
        },
        maximum_score=3,
        evidence_status="found",
    )

    assert result.status == "not_satisfied"
    assert result.awarded_score == 0


def test_numeric_threshold_requires_review_for_wrong_unit():
    result = evaluate_rule(
        rule_type="numeric_threshold",
        rule_config={
            "field": "maximum_flow_rate_l_min",
            "unit_field": "maximum_flow_rate_unit",
            "expected_unit": "L/min",
            "operator": "less_than_or_equal",
            "threshold": 5,
        },
        extracted_values={
            "maximum_flow_rate_l_min": 5,
            "maximum_flow_rate_unit": "L/s",
        },
        maximum_score=3,
        evidence_status="found",
    )

    assert result.status == "manual_review"
    assert result.awarded_score == 0
    assert result.requires_manual_review is True


def test_numeric_threshold_requires_review_for_missing_unit():
    result = evaluate_rule(
        rule_type="numeric_threshold",
        rule_config={
            "field": "maximum_flow_rate_l_min",
            "unit_field": "maximum_flow_rate_unit",
            "expected_unit": "L/min",
            "operator": "less_than_or_equal",
            "threshold": 5,
        },
        extracted_values={
            "maximum_flow_rate_l_min": 5,
        },
        maximum_score=3,
        evidence_status="found",
    )

    assert result.status == "manual_review"
    assert result.requires_manual_review is True


def test_missing_value_is_uncertain():
    result = evaluate_rule(
        rule_type="numeric_threshold",
        rule_config={
            "field":
                "maximum_flow_rate_l_min",
            "operator":
                "less_than_or_equal",
            "threshold": 5,
        },
        extracted_values={},
        maximum_score=3,
        evidence_status="not_found",
    )

    assert result.status == "uncertain"


def test_conflicting_evidence_requires_review():
    result = evaluate_rule(
        rule_type="numeric_threshold",
        rule_config={
            "field":
                "maximum_flow_rate_l_min",
            "operator":
                "less_than_or_equal",
            "threshold": 5,
        },
        extracted_values={
            "maximum_flow_rate_l_min": 5
        },
        maximum_score=3,
        evidence_status="conflicting",
    )

    assert result.status == "manual_review"
    assert result.requires_manual_review is True
