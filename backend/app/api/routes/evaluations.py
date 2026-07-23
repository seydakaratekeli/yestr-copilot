from typing import Any, cast
from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    status,
)

from app.core.auth import (
    AuthenticatedUser,
    get_current_user,
)
from app.core.supabase import (
    get_supabase_admin,
)
from app.schemas.evaluation import (
    StartEvaluationRequest,
)
from app.services.project_access_service import (
    get_accessible_project,
)
from app.services.project_evaluation_service import (
    process_project_evaluation,
)
from app.services.retry_service import (
    retry_transient,
)

router = APIRouter()

JsonRecord = dict[str, Any]


def _as_records(data: object) -> list[JsonRecord]:
    return cast(list[JsonRecord], data or [])


@router.get("/criterion-sets")
async def list_criterion_sets(
    current_user: AuthenticatedUser = Depends(
        get_current_user
    ),
) -> list[dict]:
    supabase = get_supabase_admin()

    response = retry_transient(
        lambda: (
            supabase
            .table("criterion_sets")
            .select(
                "id, code, name, version, "
                "description, status"
            )
            .eq("status", "published")
            .order("created_at", desc=True)
            .execute()
        ),
        operation_name="Kriter setlerini listeleme",
    )

    return _as_records(response.data)


@router.post(
    "/projects/{project_id}/evaluations",
    status_code=status.HTTP_202_ACCEPTED,
)
async def start_project_evaluation(
    project_id: UUID,
    request: StartEvaluationRequest,
    background_tasks: BackgroundTasks,
    current_user: AuthenticatedUser = Depends(
        get_current_user
    ),
) -> dict:
    supabase = get_supabase_admin()

    get_accessible_project(
        supabase=supabase,
        project_id=str(project_id),
        user_id=current_user.id,
    )

    criterion_set_response = retry_transient(
        lambda: (
            supabase
            .table("criterion_sets")
            .select("id, status")
            .eq(
                "id",
                request.criterion_set_id,
            )
            .eq("status", "published")
            .limit(1)
            .execute()
        ),
        operation_name="Kriter setini doğrulama",
    )

    if not criterion_set_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Yayınlanmış kriter seti "
                "bulunamadı."
            ),
        )

    insert_response = (
        supabase
        .table("project_evaluations")
        .insert(
            {
                "project_id": str(project_id),
                "criterion_set_id": (
                    request.criterion_set_id
                ),
                "created_by": current_user.id,
                "status": "queued",
            }
        )
        .execute()
    )

    if not insert_response.data:
        raise HTTPException(
            status_code=500,
            detail=(
                "Değerlendirme kaydı "
                "oluşturulamadı."
            ),
        )

    evaluation = _as_records(insert_response.data)[0]
    evaluation_id = str(evaluation["id"])

    background_tasks.add_task(
        process_project_evaluation,
        evaluation_id=evaluation_id,
    )

    return {
        "evaluation_id": evaluation_id,
        "status": "queued",
    }

@router.get(
    "/projects/{project_id}/evaluations",
)
async def list_project_evaluations(
    project_id: UUID,
    current_user: AuthenticatedUser = Depends(
        get_current_user
    ),
) -> list[dict]:
    supabase = get_supabase_admin()

    get_accessible_project(
        supabase=supabase,
        project_id=str(project_id),
        user_id=current_user.id,
    )

    response = retry_transient(
        lambda: (
            supabase
            .table("project_evaluations")
            .select(
                (
                    "id, project_id, criterion_set_id, "
                    "status, total_score, maximum_score, "
                    "score_percentage, satisfied_count, "
                    "not_satisfied_count, uncertain_count, "
                    "manual_review_count, started_at, "
                    "completed_at, error_message, created_at"
                )
            )
            .eq("project_id", str(project_id))
            .order("created_at", desc=True)
            .execute()
        ),
        operation_name="Proje değerlendirmelerini listeleme",
    )

    return _as_records(response.data)

@router.get(
    "/projects/{project_id}/evaluations/"
    "{evaluation_id}",
)
async def get_project_evaluation_detail(
    project_id: UUID,
    evaluation_id: UUID,
    current_user: AuthenticatedUser = Depends(
        get_current_user
    ),
) -> dict:
    supabase = get_supabase_admin()

    get_accessible_project(
        supabase=supabase,
        project_id=str(project_id),
        user_id=current_user.id,
    )

    evaluation_response = retry_transient(
        lambda: (
            supabase
            .table("project_evaluations")
            .select("*")
            .eq("id", str(evaluation_id))
            .eq("project_id", str(project_id))
            .limit(1)
            .execute()
        ),
        operation_name="Değerlendirme detayını okuma",
    )

    if not evaluation_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Değerlendirme bulunamadı.",
        )

    results_response = retry_transient(
        lambda: (
            supabase
            .table("project_criterion_results")
            .select(
                (
                    "id, evaluation_id, project_id, "
                    "criterion_id, rule_id, result_status, "
                    "awarded_score, maximum_score, "
                    "extracted_values, citations, "
                    "evidence_summary, missing_information, "
                    "warnings, confidence, "
                    "requires_manual_review, created_at, "
                    "criteria("
                    "code, title, category_code, "
                    "category_name, display_order"
                    ")"
                )
            )
            .eq(
                "evaluation_id",
                str(evaluation_id),
            )
            .order(
                "criteria(display_order)"
            )
            .execute()
        ),
        operation_name="Kriter sonuçlarını okuma",
    )

    evaluation = _as_records(
        evaluation_response.data
    )[0]

    return {
        "evaluation": evaluation,
        "results": _as_records(results_response.data),
    }

@router.post(
    "/projects/{project_id}/evaluations/"
    "{evaluation_id}/rerun",
    status_code=status.HTTP_202_ACCEPTED,
)
async def rerun_project_evaluation(
    project_id: UUID,
    evaluation_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: AuthenticatedUser = Depends(
        get_current_user
    ),
) -> dict[str, str]:
    supabase = get_supabase_admin()

    get_accessible_project(
        supabase=supabase,
        project_id=str(project_id),
        user_id=current_user.id,
    )

    response = retry_transient(
        lambda: (
            supabase
            .table("project_evaluations")
            .select("id, project_id, status")
            .eq("id", str(evaluation_id))
            .eq("project_id", str(project_id))
            .limit(1)
            .execute()
        ),
        operation_name="Yeniden çalıştırılacak değerlendirmeyi okuma",
    )

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Değerlendirme bulunamadı.",
        )

    evaluation = _as_records(response.data)[0]

    if evaluation["status"] in {
        "queued",
        "processing",
    }:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Değerlendirme zaten çalışıyor."
            ),
        )

    retry_transient(
        lambda: (
            supabase
            .table("project_evaluations")
            .update(
                {
                    "status": "queued",
                    "error_message": None,
                }
            )
            .eq("id", str(evaluation_id))
            .execute()
        ),
        operation_name="Değerlendirmeyi kuyruğa alma",
    )

    background_tasks.add_task(
        process_project_evaluation,
        evaluation_id=str(evaluation_id),
    )

    return {
        "evaluation_id": str(evaluation_id),
        "status": "queued",
    }
