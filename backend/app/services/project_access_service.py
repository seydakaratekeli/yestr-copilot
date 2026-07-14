from fastapi import HTTPException, status
from supabase import Client


def get_accessible_project(
    *,
    supabase: Client,
    project_id: str,
    user_id: str,
) -> dict:
    try:
        response = (
            supabase
            .table("projects")
            .select(
                "id, created_by, organization_id, status"
            )
            .eq("id", project_id)
            .maybe_single()
            .execute()
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Proje bilgisi okunamadı.",
        ) from exc

    project = response.data

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proje bulunamadı.",
        )

    # MVP'de organization_id null ve proje sahibi erişimi var.
    if project["created_by"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu projeye belge yükleme yetkiniz yok.",
        )

    if project["status"] == "archived":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Arşivlenmiş projeye belge yüklenemez.",
        )

    return project