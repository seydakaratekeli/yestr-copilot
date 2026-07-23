from datetime import datetime, timezone
from typing import Any

from supabase import Client


def get_evaluation(
    *,
    supabase: Client,
    evaluation_id: str,
) -> dict[str, Any]:
    response = (
        supabase
        .table("project_evaluations")
        .select(
            (
                "id, project_id, criterion_set_id, "
                "created_by, status"
            )
        )
        .eq("id", evaluation_id)
        .limit(1)
        .execute()
    )

    if not response.data:
        raise ValueError(
            "Değerlendirme kaydı bulunamadı."
        )

    return response.data[0]


def get_published_criteria_with_rules(
    *,
    supabase: Client,
    criterion_set_id: str,
) -> list[dict[str, Any]]:
    criteria_response = (
        supabase
        .table("criteria")
        .select(
            (
                "id, criterion_set_id, code, title, "
                "description, category_code, "
                "category_name, maximum_score, "
                "is_mandatory, display_order, "
                "evaluation_prompt, "
                "required_document_types, status"
            )
        )
        .eq(
            "criterion_set_id",
            criterion_set_id,
        )
        .eq("status", "published")
        .order("display_order")
        .execute()
    )

    criteria = criteria_response.data or []

    if not criteria:
        return []

    criterion_ids = [
        criterion["id"]
        for criterion in criteria
    ]

    rules_response = (
        supabase
        .table("criterion_rules")
        .select(
            (
                "id, criterion_id, rule_type, "
                "rule_config, rule_version, status"
            )
        )
        .in_("criterion_id", criterion_ids)
        .eq("status", "published")
        .execute()
    )

    rules_by_criterion = {
        rule["criterion_id"]: rule
        for rule in (
            rules_response.data or []
        )
    }

    combined: list[dict[str, Any]] = []

    for criterion in criteria:
        combined.append(
            {
                "criterion": criterion,
                "rule": rules_by_criterion.get(
                    criterion["id"]
                ),
            }
        )

    return combined


def mark_evaluation_processing(
    *,
    supabase: Client,
    evaluation_id: str,
) -> None:
    (
        supabase
        .table("project_evaluations")
        .update(
            {
                "status": "processing",
                "started_at": datetime.now(
                    timezone.utc
                ).isoformat(),
                "completed_at": None,
                "error_message": None,
            }
        )
        .eq("id", evaluation_id)
        .execute()
    )


def delete_previous_results(
    *,
    supabase: Client,
    evaluation_id: str,
) -> None:
    (
        supabase
        .table("project_criterion_results")
        .delete()
        .eq("evaluation_id", evaluation_id)
        .execute()
    )


def insert_criterion_result(
    *,
    supabase: Client,
    payload: dict[str, Any],
) -> dict[str, Any]:
    response = (
        supabase
        .table("project_criterion_results")
        .insert(payload)
        .execute()
    )

    if not response.data:
        raise RuntimeError(
            "Kriter sonucu kaydedilemedi."
        )

    return response.data[0]


def complete_evaluation(
    *,
    supabase: Client,
    evaluation_id: str,
    totals: dict[str, Any],
) -> None:
    (
        supabase
        .table("project_evaluations")
        .update(
            {
                **totals,
                "status": "completed",
                "completed_at": datetime.now(
                    timezone.utc
                ).isoformat(),
                "error_message": None,
            }
        )
        .eq("id", evaluation_id)
        .execute()
    )


def fail_evaluation(
    *,
    supabase: Client,
    evaluation_id: str,
    message: str,
) -> None:
    (
        supabase
        .table("project_evaluations")
        .update(
            {
                "status": "failed",
                "completed_at": datetime.now(
                    timezone.utc
                ).isoformat(),
                "error_message": message[:1000],
            }
        )
        .eq("id", evaluation_id)
        .execute()
    )