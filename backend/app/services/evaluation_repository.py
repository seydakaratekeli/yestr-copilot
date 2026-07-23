import time
from datetime import datetime, timezone
from typing import Any

from supabase import Client

from app.services.retry_service import (
    is_transient_error,
    retry_transient,
)


def get_evaluation(
    *,
    supabase: Client,
    evaluation_id: str,
) -> dict[str, Any]:
    response = retry_transient(
        lambda: (
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
        ),
        operation_name="Değerlendirme kaydını okuma",
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
    criteria_response = retry_transient(
        lambda: (
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
        ),
        operation_name="Yayımlanmış kriterleri okuma",
    )

    criteria = criteria_response.data or []

    if not criteria:
        return []

    criterion_ids = [
        criterion["id"]
        for criterion in criteria
    ]

    rules_response = retry_transient(
        lambda: (
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
        ),
        operation_name="Yayımlanmış kuralları okuma",
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
    payload = {
        "status": "processing",
        "started_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "completed_at": None,
        "error_message": None,
    }

    retry_transient(
        lambda: (
            supabase
            .table("project_evaluations")
            .update(payload)
            .eq("id", evaluation_id)
            .execute()
        ),
        operation_name="Değerlendirmeyi işleniyor olarak işaretleme",
    )


def delete_previous_results(
    *,
    supabase: Client,
    evaluation_id: str,
) -> None:
    retry_transient(
        lambda: (
            supabase
            .table("project_criterion_results")
            .delete()
            .eq("evaluation_id", evaluation_id)
            .execute()
        ),
        operation_name="Önceki kriter sonuçlarını silme",
    )


def insert_criterion_result(
    *,
    supabase: Client,
    payload: dict[str, Any],
) -> dict[str, Any]:
    response = _insert_result_idempotently(
        supabase=supabase,
        payload=payload,
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
    payload = {
        **totals,
        "status": "completed",
        "completed_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "error_message": None,
    }

    retry_transient(
        lambda: (
            supabase
            .table("project_evaluations")
            .update(payload)
            .eq("id", evaluation_id)
            .execute()
        ),
        operation_name="Değerlendirmeyi tamamlama",
    )


def fail_evaluation(
    *,
    supabase: Client,
    evaluation_id: str,
    message: str,
) -> None:
    payload = {
        "status": "failed",
        "completed_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "error_message": message[:1000],
    }

    retry_transient(
        lambda: (
            supabase
            .table("project_evaluations")
            .update(payload)
            .eq("id", evaluation_id)
            .execute()
        ),
        operation_name="Değerlendirmeyi başarısız işaretleme",
    )


def _insert_result_idempotently(
    *,
    supabase: Client,
    payload: dict[str, Any],
    attempts: int = 3,
) -> Any:
    for attempt in range(1, attempts + 1):
        try:
            return (
                supabase
                .table("project_criterion_results")
                .insert(payload)
                .execute()
            )

        except Exception as exc:
            if not is_transient_error(exc):
                raise

            existing = retry_transient(
                lambda: (
                    supabase
                    .table("project_criterion_results")
                    .select("*")
                    .eq(
                        "evaluation_id",
                        payload["evaluation_id"],
                    )
                    .eq(
                        "criterion_id",
                        payload["criterion_id"],
                    )
                    .limit(1)
                    .execute()
                ),
                operation_name=(
                    "Eklenen kriter sonucunu doğrulama"
                ),
            )

            if existing.data:
                return existing

            if attempt == attempts:
                raise

            time.sleep(
                0.5 * (2 ** (attempt - 1))
            )

    raise RuntimeError(
        "Kriter sonucu ekleme beklenmedik şekilde sonlandı."
    )
